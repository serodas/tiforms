import os
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings


class UploadedFile:
    def handle_uploaded_files(self, files, request=None):
        """
        Recibe una lista de UploadedFile y devuelve lista de URLs absolutas.
        """
        file_urls = []

        for f in files:
            ext = os.path.splitext(f.name)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            full_path = unique_name

            default_storage.save(full_path, ContentFile(f.read()))

            absolute_url = self.build_absolute_url(full_path, request)
            file_urls.append(absolute_url)

        return file_urls

    def build_absolute_url(self, file_path, request=None):
        """
        Construye la URL absoluta con HTTPS para el archivo.
        """
        relative_url = f"{settings.MEDIA_URL}{file_path}"

        if request:
            absolute_url = request.build_absolute_uri(relative_url)
        else:
            absolute_url = self.build_absolute_url_manual(relative_url)

        return absolute_url

    def build_absolute_url_manual(self, relative_url):
        """
        Construye URL absoluta manualmente SIN usar django.contrib.sites
        """
        domain = getattr(settings, "DOMAIN", None)

        if not domain:
            if settings.ALLOWED_HOSTS:
                domain = f"{settings.ALLOWED_HOSTS[0]}:8000"
            else:
                domain = "localhost:8000"

        domain = domain.replace("http://", "").replace("https://", "")

        use_https = getattr(settings, "USE_HTTPS", not settings.DEBUG)
        protocol = "https" if use_https else "http"

        absolute_url = f"{protocol}://{domain}{relative_url}"

        return absolute_url
