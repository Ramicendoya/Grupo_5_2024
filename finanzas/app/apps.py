from django.apps import AppConfig


class AppConfig(AppConfig):
    """
    Configuración de la aplicación MyApp.

    Esta clase se encarga de configurar la aplicación MyApp.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"