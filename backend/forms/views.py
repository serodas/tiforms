import json
from .models import Form, FormField, FormSubmission
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import FormSerializer, FormFieldSerializer, FormSubmissionSerializer


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all().order_by("-created_at")
    serializer_class = FormSerializer


class FormFieldViewSet(viewsets.ModelViewSet):
    queryset = FormField.objects.all().order_by("-created_at")
    serializer_class = FormFieldSerializer


class FormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = FormSubmission.objects.all().order_by("-created_at")
    serializer_class = FormSubmissionSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        form_id = data.get("form_id") or data.get("form")

        if not form_id:
            return Response(
                {"error": "form_id es obligatorio"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response(
                {"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        submission_data = {}

        # Campos de texto, fechas, etc.
        for key, value in data.items():
            if key != "form_id" and key != "form":
                submission_data[key] = value

        # Archivos (documentos, firmas, fotos) de forma dinámica
        for key in request.FILES:
            files = request.FILES.getlist(
                key
            )  # Esto devuelve todos los archivos con ese nombre
            if len(files) == 1:
                submission_data[key] = files[0].name  # o sube a storage y guarda la URL
            else:
                submission_data[key] = [f.name for f in files]

        # Guardar en la base
        serializer = self.get_serializer(
            data={"form": form.id, "data": json.dumps(submission_data)}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@api_view(["GET"])
def health_check(request):
    return Response({"data": "ok"})
