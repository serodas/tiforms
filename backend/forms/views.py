from django.shortcuts import render
from django.http import JsonResponse
from .models import Transaccion
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def test_connection_ibmi(request):
    forms = Transaccion.objects.all()[:10]

    # Convertir a lista de diccionarios
    data = [
        {
            "name": f.num_factura,
            "description": f.tipo_nota,
        }
        for f in forms
    ]

    return JsonResponse(data, safe=False)


@api_view(["GET"])
def health_check(request):
    return Response({"data": "ok"})
