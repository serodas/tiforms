from .models import Form, FormField, FormSubmission
from rest_framework import viewsets
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


@api_view(["GET"])
def health_check(request):
    return Response({"data": "ok"})
