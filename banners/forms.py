from django import forms

from .models import Banner


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = (
            "title",
            "description",
            "icon",
            "button_text",
            "button_url",
            "position",
            "is_active",
        )
        labels = {
            "title": "Título",
            "description": "Descripción",
            "icon": "Ícono",
            "button_text": "Texto del enlace",
            "button_url": "Destino del enlace",
            "position": "Posición",
            "is_active": "Mostrar en el sitio",
        }
        help_texts = {
            "button_url": (
                "Acepta enlaces https://, rutas internas como /accounts/registro/ "
                "o secciones como #contacto."
            ),
            "position": "Los números menores aparecen primero.",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Ej. Reserva tu lugar"}
            ),
            "button_text": forms.TextInput(
                attrs={"placeholder": "Ej. Quiero asistir"}
            ),
            "button_url": forms.TextInput(
                attrs={"placeholder": "Ej. #contacto"}
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }
