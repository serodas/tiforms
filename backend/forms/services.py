import os
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def handle_uploaded_files(files):
    """
    Recibe una lista de UploadedFile y devuelve lista de URLs.
    Guarda los archivos en disco por fecha con nombres únicos.
    """
    file_urls = []
    today = datetime.today()
    folder_path = f"uploads/{today.year}/{today.month:02}/{today.day:02}/"
    os.makedirs(os.path.join(default_storage.location, folder_path), exist_ok=True)

    for f in files:
        ext = os.path.splitext(f.name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        full_path = os.path.join(folder_path, unique_name)
        default_storage.save(full_path, ContentFile(f.read()))
        file_urls.append(default_storage.url(full_path))

    return file_urls
