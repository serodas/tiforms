import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class DocumentosUsuariosCmeView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post(self, req, *args, **kwargs):
        try:
            json_data = req.data

            documentos_config = [
                {
                    "nombre": "autorizacion",
                    "url": json_data.get("img_autorizacion"),
                    "tipoDocumento": "AU",
                    "observacion": "Autorización para procedimiento",
                    "campo_archivo": "documento",
                },
                {
                    "nombre": "orden_medica",
                    "url": json_data.get("img_orden"),
                    "tipoDocumento": "OM",
                    "observacion": "Orden médica del procedimiento",
                    "campo_archivo": "documento",
                },
            ]

            responses = []
            api_url = "https://cme_php/app_dev.php/api/documentos/usuarios"

            for doc_config in documentos_config:
                doc_url = doc_config["url"]

                if not doc_url:
                    continue

                try:
                    file_data = self.download_file_from_url(doc_url)

                    form_data = {
                        "beneficiarioId": json_data.get("benumdocbe", ""),
                        "servicioId": "5",
                        "tipoDocumento": doc_config["tipoDocumento"],
                        "observacion": doc_config["observacion"],
                        "usuario": "FORMS",
                        "interno": json_data.get("mrcodcons", ""),
                    }

                    files = {doc_config["campo_archivo"]: file_data}

                    headers = {
                        "Host": "localhost",
                        "User-Agent": "Django-App/1.0",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip, deflate, br",
                    }

                    response = requests.post(
                        api_url,
                        data=form_data,
                        files=files,
                        headers=headers,
                        timeout=30,
                        verify=False,
                    )

                    if response.status_code in [200, 201]:
                        responses.append(
                            {
                                "documento": doc_config["nombre"],
                                "success": True,
                                "status_code": response.status_code,
                            }
                        )
                    else:
                        responses.append(
                            {
                                "documento": doc_config["nombre"],
                                "success": False,
                                "status_code": response.status_code,
                                "error": response.text,
                            }
                        )

                except requests.exceptions.RequestException as re:
                    responses.append(
                        {
                            "documento": doc_config["nombre"],
                            "tipo_documento": doc_config["tipoDocumento"],
                            "success": False,
                            "error": f"Error de conexión: {str(re)}",
                        }
                    )
                except Exception as e:
                    responses.append(
                        {
                            "documento": doc_config["nombre"],
                            "tipo_documento": doc_config["tipoDocumento"],
                            "success": False,
                            "error": str(e),
                        }
                    )

            return self._build_final_response(responses)

        except Exception as e:
            return Response(
                {"error": f"Error interno: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def download_file_from_url(self, url):
        """
        Descarga un archivo desde una URL y lo prepara para enviar en form-data
        """
        try:

            headers = {"User-Agent": "Django-App/1.0"}

            response = requests.get(url, verify=False, headers=headers, timeout=30)
            response.raise_for_status()

            filename = os.path.basename(url.split("?")[0])

            _, ext = os.path.splitext(filename)
            if not ext:
                content_type = response.headers.get("content-type", "")
                if "image/png" in content_type:
                    ext = ".png"
                elif "image/jpeg" in content_type:
                    ext = ".jpg"
                elif "image/gif" in content_type:
                    ext = ".gif"
                elif "application/pdf" in content_type:
                    ext = ".pdf"
                else:
                    ext = ".bin"

                filename = f"documento{ext}"

            return (
                filename,
                response.content,
                response.headers.get("content-type", "application/octet-stream"),
            )

        except Exception as e:
            raise Exception(f"No se pudo descargar el archivo: {str(e)}")

    def _build_final_response(self, responses):
        """Construye la respuesta final basada en los resultados de las subidas"""
        successful = [r for r in responses if r.get("success")]
        failed = [r for r in responses if not r.get("success")]
        total = len(responses)

        if not responses:
            return Response(
                {"status": "error", "message": "No se procesaron documentos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if failed and not successful:
            return Response(
                {
                    "status": "error",
                    "message": "Todos los documentos fallaron",
                    "failed_uploads": failed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if failed and successful:
            return Response(
                {
                    "status": "partial_success",
                    "message": f"Éxito: {len(successful)}/{total} documentos",
                    "successful_uploads": successful,
                    "failed_uploads": failed,
                },
                status=status.HTTP_207_MULTI_STATUS,
            )

        return Response(
            {
                "status": "success",
                "message": f"Todos los {total} documentos subidos exitosamente",
                "uploads": successful,
            },
            status=status.HTTP_201_CREATED,
        )
