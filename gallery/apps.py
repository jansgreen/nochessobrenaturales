from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gallery"
    verbose_name = "Galería de imágenes"

    def ready(self):
        from . import signals  # noqa: F401

