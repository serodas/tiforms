# forms/views/mixins.py
from rest_framework import serializers
from ..decorators import get_model_by_name, get_registered_models


class DynamicSerializerMixin:
    """
    Mixin que obtiene el modelo y crea el serializer dinámicamente
    """

    def get_model_class(self):
        """
        Obtiene la clase del modelo desde el parámetro de URL 'model_name'
        """
        # self.kwargs contiene los parámetros de la URL
        model_name = self.kwargs.get("model_name")

        if not model_name:
            raise ValueError("No se especificó el nombre del modelo en la URL")

        # Busca el modelo en el registro de decoradores
        model_class = get_model_by_name(model_name)

        if not model_class:
            available_models = list(get_registered_models().keys())
            raise ValueError(
                f'Modelo "{model_name}" no encontrado. Modelos disponibles: {available_models}'
            )

        return model_class

    def get_serializer_class(self):
        """
        Crea un serializer dinámico para el modelo específico
        """
        model_class = self.get_model_class()

        # Crear serializer dinámico
        DynamicSerializer = type(
            f"Dynamic{model_class.__name__}Serializer",
            (serializers.ModelSerializer,),
            {"Meta": type("Meta", (), {"model": model_class, "fields": "__all__"})},
        )

        return DynamicSerializer
