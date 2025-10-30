from ..models import Form, FormField
from rest_framework import viewsets
from ..serializers import FormSerializer, FormFieldSerializer, FormSubmissionSerializer


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all().order_by("-created_at")
    serializer_class = FormSerializer


class FormFieldViewSet(viewsets.ModelViewSet):
    queryset = FormField.objects.all().order_by("-created_at")
    serializer_class = FormFieldSerializer
