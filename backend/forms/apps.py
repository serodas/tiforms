from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "forms"

    def ready(self):
        """
        Importar señales y listeners cuando la app esté lista
        """
        import forms.signals.webhook_signals
        import forms.listeners.webhook_listeners
        import forms.models.soporte_fomag
