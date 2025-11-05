from django.urls import path, include

from forms.views.consecutivos_recibos import ConsecutivosRecibosView
from forms.views.beneficiarios import BeneficiarioView
from forms.views.health_check import health_check
from forms.views.submissions import FormSubmissionCreateAPIView

from forms.views.forms import FormViewSet, FormFieldViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"forms", FormViewSet)
router.register(r"fields", FormFieldViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "submissions/", FormSubmissionCreateAPIView.as_view(), name="form-submissions"
    ),
    path("beneficiarios/", BeneficiarioView.as_view(), name="beneficiarios"),
    path(
        "consecutivos/recibos/",
        ConsecutivosRecibosView.as_view(),
        name="consecutivos-recibos",
    ),
    path("healthz/", health_check, name="health-check"),
]
