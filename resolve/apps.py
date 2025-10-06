from django.apps import AppConfig


class ResolveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resolve'
    
    def ready(self):
        import resolve.signals