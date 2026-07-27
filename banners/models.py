import html
from urllib.parse import urlsplit

import nh3
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django_ckeditor_5.fields import CKEditor5Field


ALLOWED_DESCRIPTION_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "blockquote",
    "h2",
    "h3",
    "a",
}
ALLOWED_DESCRIPTION_ATTRIBUTES = {
    "a": {"href", "title", "target"},
}


def sanitize_banner_description(value):
    return nh3.clean(
        value,
        tags=ALLOWED_DESCRIPTION_TAGS,
        attributes=ALLOWED_DESCRIPTION_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )


def validate_banner_url(value):
    if not value:
        return

    if value.startswith("#"):
        return

    if value.startswith("/") and not value.startswith("//"):
        return

    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return

    raise ValidationError(
        "Usa una URL http(s), una ruta interna que comience con / "
        "o una sección que comience con #."
    )


class Banner(models.Model):
    class Icon(models.TextChoices):
        STAR = "star", "Estrella"
        HEART = "heart", "Corazón"
        PEOPLE = "people", "Comunidad"
        BOOK = "book", "Biblia"
        CALENDAR = "calendar", "Calendario"
        CROSS = "cross", "Cruz"

    title = models.CharField(max_length=120)
    description = CKEditor5Field(
        max_length=3000,
        config_name="banner_description",
    )
    icon = models.CharField(
        max_length=20,
        choices=Icon.choices,
        default=Icon.STAR,
    )
    button_text = models.CharField(max_length=60, blank=True)
    button_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[validate_banner_url],
    )
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "id")
        verbose_name = "banner"
        verbose_name_plural = "banners"

    def clean(self):
        super().clean()
        self.description = sanitize_banner_description(self.description)
        description_text = html.unescape(strip_tags(self.description))
        if not description_text.replace("\xa0", " ").strip():
            raise ValidationError(
                {"description": "La descripción debe contener texto."}
            )
        if bool(self.button_text.strip()) != bool(self.button_url.strip()):
            raise ValidationError(
                "El texto y el destino del enlace deben completarse juntos."
            )

    def __str__(self):
        return self.title
