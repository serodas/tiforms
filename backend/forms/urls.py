from django.urls import path, include

from .views import health_check, FormViewSet, FormFieldViewSet, FormSubmissionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"forms", FormViewSet)
router.register(r"fields", FormFieldViewSet)
router.register(r"submissions", FormSubmissionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("healthz/", health_check),
]
