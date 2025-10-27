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
        # Copiar los datos del request
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

        # Construir JSON para almacenar en TextField
        submission_data = {}

        # Campos normales (valores de texto)
        for key, value in data.items():
            if key != "form_id" and key != "form":
                submission_data[key] = value

        # Archivos y firmas
        for key, file in request.FILES.items():
            # Puedes guardar solo el nombre del archivo, o subir a storage y guardar URL
            # Por simplicidad, guardamos el nombre
            submission_data[key] = file.name

        # Serializar y guardar
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
