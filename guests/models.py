from pathlib import Path
from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def guest_photo_upload_to(instance, filename):
    extension = Path(filename).suffix.lower()
    dated_folder = timezone.now().strftime("%Y/%m")
    return f"guests/{dated_folder}/{uuid4().hex}{extension}"


class ShowcaseCategory(models.Model):
    title = models.CharField(max_length=120)
    headline = models.CharField(max_length=170)
    accent = models.CharField(max_length=170, blank=True)
    description = models.TextField(max_length=500)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "title", "id")
        verbose_name = "categoría destacada"
        verbose_name_plural = "categorías destacadas"

    def __str__(self):
        return self.title


class ShowcaseItem(models.Model):
    category = models.ForeignKey(
        ShowcaseCategory,
        on_delete=models.CASCADE,
        related_name="items",
    )
    name = models.CharField(max_length=140)
    role = models.CharField(max_length=140, blank=True)
    description = models.TextField(max_length=360)
    photo = models.ImageField(
        upload_to=guest_photo_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp")
            )
        ],
    )
    alt_text = models.CharField(max_length=180)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "name", "id")
        verbose_name = "tarjeta destacada"
        verbose_name_plural = "tarjetas destacadas"

    def __str__(self):
        return self.name
