from forms.services.consecutivos_recibos_service import (
    ConsecutivosRecibosService,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ConsecutivosRecibosView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.consecutivos_recibos_service = ConsecutivosRecibosService()

    def get(self, request):
        try:
            search_param = request.GET.get("search", "").strip()
            consecutivos = self.consecutivos_recibos_service.search(search_param)

            return Response({"results": consecutivos})

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
