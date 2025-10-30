from forms.services.beneficiario_service import BeneficiarioService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class BeneficiarioView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.beneficiario_service = BeneficiarioService()

    def get(self, request):
        try:
            search_param = request.GET.get("search", "").strip()
            beneficiario = self.beneficiario_service.search(search_param)

            if beneficiario:
                return Response({"results": beneficiario})
            else:
                return Response(
                    {"error": "Beneficiario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
