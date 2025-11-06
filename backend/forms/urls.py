from django.urls import path, include

from forms.views.submission_task_log import (
    SubmissionTaskLogByWebhookAPIView,
    SubmissionTaskLogDetailAPIView,
    SubmissionTaskLogListAPIView,
)
from forms.views.webhook_config import (
    WebhookConfigByFormAPIView,
    WebhookConfigDetailAPIView,
    WebhookConfigListAPIView,
)
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
    path("webhooks/", WebhookConfigListAPIView.as_view(), name="api-webhook-list"),
    path(
        "webhooks/<int:pk>/",
        WebhookConfigDetailAPIView.as_view(),
        name="api-webhook-detail",
    ),
    path(
        "webhooks/by-form/<int:form_id>/",
        WebhookConfigByFormAPIView.as_view(),
        name="api-webhook-by-form",
    ),
    path(
        "task-logs/",
        SubmissionTaskLogListAPIView.as_view(),
        name="api-task-log-list",
    ),
    path(
        "task-logs/<int:pk>/",
        SubmissionTaskLogDetailAPIView.as_view(),
        name="api-task-log-detail",
    ),
    path(
        "task-logs/by-webhook/<int:webhook_id>/",
        SubmissionTaskLogByWebhookAPIView.as_view(),
        name="api-task-log-by-webhook",
    ),
    path("healthz/", health_check, name="health-check"),
]
