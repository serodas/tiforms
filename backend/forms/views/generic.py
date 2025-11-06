from rest_framework import generics, status
from rest_framework.response import Response
from .mixins import DynamicSerializerMixin


class GenericModelCreateView(DynamicSerializerMixin, generics.CreateAPIView):
    """
    Vista genérica para CREAR recursos
    Endpoints:
    - POST /api/{model_name}/
    """

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "success": True,
                    "message": "Recurso creado exitosamente",
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
