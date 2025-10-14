from django.apps import AppConfig


class VentaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.venta'

    def ready(self):
        import applications.venta.signals  # 👈 importa los signals