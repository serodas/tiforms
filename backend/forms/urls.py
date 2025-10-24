from django.urls import path

from .views import health_check, test_connection_ibmi

urlpatterns = [
    path("healthz/", health_check),
    path("tiforms/", test_connection_ibmi, name="list_tiforms"),
]
