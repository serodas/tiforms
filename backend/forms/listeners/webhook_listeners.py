import json
import requests
from django.dispatch import receiver
from django.utils import timezone
from forms.models.forms import WebhookConfig, SubmissionTaskLog
from forms.signals.webhook_signals import submission_created


@receiver(submission_created)
def handle_new_submission(sender, submission, **kwargs):
    """
    Listener síncrono para nuevas submissions
    """
    print(f"🎯 Evento recibido: Nueva submission {submission.id}")

    # Buscar webhooks activos para este formulario
    webhooks = WebhookConfig.objects.filter(form=submission.form, is_active=True)

    print(f"🔍 Encontrados {webhooks.count()} webhooks activos")

    # Procesar cada webhook de forma síncrona
    for webhook in webhooks:
        print(f"🚀 Procesando webhook: {webhook.name}")
        process_webhook_sync(webhook, submission)


def process_webhook_sync(webhook, submission):
    """
    Procesar webhook de forma síncrona
    """
    # Crear log de tarea
    task_log = SubmissionTaskLog.objects.create(
        submission=submission,
        webhook=webhook,
        status="running",
        attempt=1,
        started_at=timezone.now(),
    )

    try:
        # Preparar el request
        payload = {
            "event_type": "form_submission",
            "submission_id": submission.id,
            "form_id": submission.form.id,
            "form_name": submission.form.name,
            "submitted_at": timezone.now().isoformat(),
            "data": "{}",  # Aquí irían los datos reales del formulario
        }

        # Preparar headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "WebhookSystem/1.0",
        }

        # Agregar headers personalizados del webhook
        custom_headers = webhook.headers_dict
        if custom_headers:
            headers.update(custom_headers)

        print(f"🌐 Enviando a: {webhook.url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        print(f"📋 Headers: {headers}")

        # Hacer la petición HTTP (síncrona)
        response = requests.post(
            webhook.url, json=payload, headers=headers, timeout=webhook.timeout
        )

        # Guardar respuesta
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text[:1000],  # Limitar tamaño
        }

        # Determinar estado
        if response.status_code in [200, 201, 202]:
            task_log.status = "success"
            print(f"✅ Webhook exitoso - Status: {response.status_code}")
        else:
            task_log.status = "failed"
            task_log.error_message = (
                f"HTTP {response.status_code}: {response.text[:500]}"
            )
            print(f"❌ Webhook fallido - Status: {response.status_code}")

        task_log.response_data = json.dumps(response_data)
        task_log.completed_at = timezone.now()
        task_log.save()

        return True

    except requests.exceptions.Timeout:
        error_msg = f"Timeout después de {webhook.timeout} segundos"
        handle_webhook_error(task_log, error_msg)
        return False

    except requests.exceptions.ConnectionError:
        error_msg = "Error de conexión - No se pudo alcanzar la URL"
        handle_webhook_error(task_log, error_msg)
        return False

    except requests.exceptions.RequestException as e:
        error_msg = f"Error en la petición: {str(e)}"
        handle_webhook_error(task_log, error_msg)
        return False

    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        handle_webhook_error(task_log, error_msg)
        return False


def handle_webhook_error(task_log, error_message):
    """
    Manejar errores del webhook
    """
    task_log.status = "failed"
    task_log.error_message = error_message
    task_log.completed_at = timezone.now()
    task_log.save()
    print(f"💥 Error: {error_message}")
