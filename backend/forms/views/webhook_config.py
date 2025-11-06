from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from forms.models.forms import WebhookConfig, SubmissionTaskLog
from forms.serializers.forms import WebhookConfigSerializer
import json


class WebhookConfigListAPIView(APIView):
    """
    API para listar y crear WebhookConfig
    """

    def get(self, request):
        webhooks = WebhookConfig.objects.select_related("form").all()
        serializer = WebhookConfigSerializer(webhooks, many=True)
        return Response({"status": "success", "data": serializer.data})

    def post(self, request):
        serializer = WebhookConfigSerializer(data=request.data)
        if serializer.is_valid():
            webhook = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Webhook creado exitosamente",
                    "data": WebhookConfigSerializer(webhook).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class WebhookConfigDetailAPIView(APIView):
    """
    API para obtener, actualizar y eliminar un WebhookConfig específico
    """

    def get_object(self, pk):
        return get_object_or_404(WebhookConfig, pk=pk)

    def get(self, request, pk):
        webhook = self.get_object(pk)
        serializer = WebhookConfigSerializer(webhook)
        return Response({"status": "success", "data": serializer.data})

    def put(self, request, pk):
        webhook = self.get_object(pk)
        serializer = WebhookConfigSerializer(webhook, data=request.data)
        if serializer.is_valid():
            updated_webhook = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Webhook actualizado exitosamente",
                    "data": WebhookConfigSerializer(updated_webhook).data,
                }
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        webhook = self.get_object(pk)
        serializer = WebhookConfigSerializer(webhook, data=request.data, partial=True)
        if serializer.is_valid():
            updated_webhook = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Webhook actualizado parcialmente",
                    "data": WebhookConfigSerializer(updated_webhook).data,
                }
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        webhook = self.get_object(pk)
        webhook_name = webhook.name
        webhook.delete()
        return Response(
            {
                "status": "success",
                "message": f'Webhook "{webhook_name}" eliminado exitosamente',
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class WebhookConfigByFormAPIView(APIView):
    """
    API para obtener webhooks por formulario
    """

    def get(self, request, form_id):
        webhooks = WebhookConfig.objects.filter(form_id=form_id, is_active=True)
        serializer = WebhookConfigSerializer(webhooks, many=True)
        return Response(
            {"status": "success", "count": webhooks.count(), "data": serializer.data}
        )
