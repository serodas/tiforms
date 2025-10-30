import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Form
from ..serializers import FormSubmissionSerializer
from ..services import uploaded_file


class FormSubmissionCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        form_id = request.data.get("form_id") or request.data.get("form")

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

        for key, value in request.data.items():
            if key not in ["form_id", "form"]:
                submission_data[key] = value

        for key in request.FILES:
            files = request.FILES.getlist(key)
            urls = uploaded_file(files)
            submission_data[key] = urls[0] if len(urls) == 1 else urls

        serializer = FormSubmissionSerializer(
            data={"form": form.id, "data": json.dumps(submission_data)}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
