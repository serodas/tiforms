import os
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings


class UploadedFile:
    def handle_uploaded_files(self, files):
        """
        Recibe una lista de UploadedFile y devuelve lista de URLs.
        Guarda los archivos directamente en uploads/ con nombres únicos.
        """
        file_urls = []

        for f in files:
            ext = os.path.splitext(f.name)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            full_path = unique_name  # Guardar directamente en uploads/

            # Guardar archivo
            default_storage.save(full_path, ContentFile(f.read()))

            # URL accesible
            file_urls.append(settings.MEDIA_URL + full_path)

        return file_urls
