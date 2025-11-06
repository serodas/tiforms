from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from forms.models.forms import WebhookConfig, SubmissionTaskLog
from forms.serializers.forms import SubmissionTaskLogSerializer
import json


class SubmissionTaskLogListAPIView(APIView):
    """
    API para listar y crear SubmissionTaskLog
    """

    def get(self, request):
        task_logs = SubmissionTaskLog.objects.select_related(
            "submission", "webhook"
        ).all()

        # Filtros opcionales
        webhook_id = request.GET.get("webhook_id")
        status_filter = request.GET.get("status")
        submission_id = request.GET.get("submission_id")

        if webhook_id:
            task_logs = task_logs.filter(webhook_id=webhook_id)
        if status_filter:
            task_logs = task_logs.filter(status=status_filter)
        if submission_id:
            task_logs = task_logs.filter(submission_id=submission_id)

        serializer = SubmissionTaskLogSerializer(task_logs, many=True)
        return Response(
            {"status": "success", "count": task_logs.count(), "data": serializer.data}
        )

    def post(self, request):
        serializer = SubmissionTaskLogSerializer(data=request.data)
        if serializer.is_valid():
            task_log = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Log de tarea creado exitosamente",
                    "data": SubmissionTaskLogSerializer(task_log).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubmissionTaskLogDetailAPIView(APIView):
    """
    API para obtener, actualizar y eliminar un SubmissionTaskLog específico
    """

    def get_object(self, pk):
        return get_object_or_404(SubmissionTaskLog, pk=pk)

    def get(self, request, pk):
        task_log = self.get_object(pk)
        serializer = SubmissionTaskLogSerializer(task_log)
        return Response({"status": "success", "data": serializer.data})

    def put(self, request, pk):
        task_log = self.get_object(pk)
        serializer = SubmissionTaskLogSerializer(task_log, data=request.data)
        if serializer.is_valid():
            updated_task_log = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Log de tarea actualizado exitosamente",
                    "data": SubmissionTaskLogSerializer(updated_task_log).data,
                }
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        task_log = self.get_object(pk)
        serializer = SubmissionTaskLogSerializer(
            task_log, data=request.data, partial=True
        )
        if serializer.is_valid():
            updated_task_log = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Log de tarea actualizado parcialmente",
                    "data": SubmissionTaskLogSerializer(updated_task_log).data,
                }
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubmissionTaskLogByWebhookAPIView(APIView):
    """
    API para obtener logs de tareas por webhook
    """

    def get(self, request, webhook_id):
        task_logs = SubmissionTaskLog.objects.filter(webhook_id=webhook_id)

        status_filter = request.GET.get("status")
        if status_filter:
            task_logs = task_logs.filter(status=status_filter)

        task_logs = task_logs.order_by("-started_at")

        serializer = SubmissionTaskLogSerializer(task_logs, many=True)
        return Response(
            {"status": "success", "count": task_logs.count(), "data": serializer.data}
        )
