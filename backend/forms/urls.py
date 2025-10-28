from django.urls import path, include

from .views_submissions import FormSubmissionCreateAPIView

from .views import health_check, FormViewSet, FormFieldViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"forms", FormViewSet)
router.register(r"fields", FormFieldViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "submissions/", FormSubmissionCreateAPIView.as_view(), name="form-submissions"
    ),
    path("healthz/", health_check),
]
