from pathlib import Path
from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def gallery_image_upload_to(instance, filename):
    extension = Path(filename).suffix.lower()
    dated_folder = timezone.now().strftime("%Y/%m")
    return f"gallery/{dated_folder}/{uuid4().hex}{extension}"


class GalleryImage(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField(max_length=600, blank=True)
    image = models.ImageField(
        upload_to=gallery_image_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp")
            )
        ],
    )
    alt_text = models.CharField(max_length=180)
    photographed_on = models.DateField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "-photographed_on", "-created_at")
        verbose_name = "imagen de galería"
        verbose_name_plural = "imágenes de galería"

    def __str__(self):
        return self.title

