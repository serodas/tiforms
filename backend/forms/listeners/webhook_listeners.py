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

    webhooks = WebhookConfig.objects.filter(form=submission.form, is_active=True)

    for webhook in webhooks:
        process_webhook_sync(webhook, submission)


def process_webhook_sync(webhook, submission):
    """
    Procesar webhook de forma síncrona
    """
    task_log = SubmissionTaskLog.objects.create(
        submission=submission,
        webhook=webhook,
        status="running",
        attempt=1,
        started_at=timezone.now(),
    )

    try:
        payload = {
            "event_type": "form_submission",
            "submission_id": submission.id,
            "form_id": submission.form.id,
            "form_name": submission.form.name,
            "submitted_at": timezone.now().isoformat(),
            "data": submission.data,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "WebhookSystem/1.0",
        }

        custom_headers = webhook.headers_dict
        if custom_headers:
            headers.update(custom_headers)

        response = requests.post(
            webhook.url,
            json=json.loads(str(payload.get("data"))),
            headers=headers,
            timeout=webhook.timeout,
        )

        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text[:1000],
        }

        if response.status_code in [200, 201, 202]:
            task_log.status = "success"
        else:
            task_log.status = "failed"
            task_log.error_message = (
                f"HTTP {response.status_code}: {response.text[:500]}"
            )

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
