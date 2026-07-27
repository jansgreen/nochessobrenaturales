from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db import models


def validate_paypal_url(value):
    if not value:
        return

    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise ValidationError("Ingresa un enlace válido de PayPal.") from error

    hostname = (parsed.hostname or "").lower().rstrip(".")
    is_paypal_host = (
        hostname == "paypal.com"
        or hostname.endswith(".paypal.com")
        or hostname == "paypal.me"
        or hostname.endswith(".paypal.me")
    )

    if (
        parsed.scheme.lower() != "https"
        or not is_paypal_host
        or parsed.username
        or parsed.password
        or port not in (None, 443)
    ):
        raise ValidationError(
            "Usa un enlace seguro de paypal.com o paypal.me."
        )


class DonationSettings(models.Model):
    paypal_url = models.URLField(
        "enlace de PayPal",
        max_length=500,
        blank=True,
        validators=[validate_paypal_url],
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuración de donaciones"
        verbose_name_plural = "configuración de donaciones"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuración de donaciones"

