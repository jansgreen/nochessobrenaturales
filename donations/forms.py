from django import forms

from .models import DonationSettings


class DonationSettingsForm(forms.ModelForm):
    class Meta:
        model = DonationSettings
        fields = ("paypal_url",)
        labels = {
            "paypal_url": "Enlace para recibir donaciones",
        }
        help_texts = {
            "paypal_url": (
                "Pega un enlace https:// de paypal.com o paypal.me. "
                "Déjalo vacío para ocultar el botón de donaciones."
            ),
        }
        widgets = {
            "paypal_url": forms.URLInput(
                attrs={
                    "placeholder": (
                        "https://www.paypal.com/donate/"
                        "?hosted_button_id=..."
                    ),
                    "autocomplete": "off",
                    "spellcheck": "false",
                }
            ),
        }

