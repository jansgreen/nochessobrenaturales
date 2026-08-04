from django import forms

from .models import Banner, sanitize_banner_description


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = (
            "title_es",
            "description_es",
            "button_text_es",
            "title_en",
            "description_en",
            "button_text_en",
            "title_pt",
            "description_pt",
            "button_text_pt",
            "icon",
            "button_url",
            "position",
            "is_active",
        )
        labels = {
            "title_es": "Título",
            "description_es": "Descripción",
            "button_text_es": "Texto del enlace",
            "title_en": "Title",
            "description_en": "Description",
            "button_text_en": "Link text",
            "title_pt": "Título",
            "description_pt": "Descrição",
            "button_text_pt": "Texto do link",
            "icon": "Ícono",
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
            "title_es": forms.TextInput(
                attrs={"placeholder": "Ej. Reserva tu lugar"}
            ),
            "button_text_es": forms.TextInput(
                attrs={"placeholder": "Ej. Quiero asistir"}
            ),
            "title_en": forms.TextInput(
                attrs={"placeholder": "E.g. Reserve your place"}
            ),
            "button_text_en": forms.TextInput(
                attrs={"placeholder": "E.g. I want to attend"}
            ),
            "title_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Reserve o seu lugar"}
            ),
            "button_text_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Quero participar"}
            ),
            "button_url": forms.TextInput(
                attrs={"placeholder": "Ej. #contacto"}
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("title", "description", "button_text"):
                if base_name not in data:
                    continue
                for suffix in ("es", "en", "pt"):
                    localized_name = f"{base_name}_{suffix}"
                    if localized_name not in data:
                        data[localized_name] = data.get(base_name, "")
            if args:
                args = (data, *args[1:])
            else:
                kwargs["data"] = data
        super().__init__(*args, **kwargs)
        for suffix in ("es", "en", "pt"):
            self.fields[f"title_{suffix}"].required = True
            self.fields[f"description_{suffix}"].required = True

    def clean(self):
        cleaned_data = super().clean()
        for suffix in ("es", "en", "pt"):
            field_name = f"description_{suffix}"
            description = cleaned_data.get(field_name)
            if description:
                cleaned_data[field_name] = sanitize_banner_description(
                    description
                )

        button_url = (cleaned_data.get("button_url") or "").strip()
        button_texts = [
            (cleaned_data.get(f"button_text_{suffix}") or "").strip()
            for suffix in ("es", "en", "pt")
        ]
        if button_url and not all(button_texts):
            raise forms.ValidationError(
                "Completa el texto del enlace en los tres idiomas."
            )
        if any(button_texts) and not button_url:
            raise forms.ValidationError(
                "Agrega el destino para el enlace del banner."
            )
        return cleaned_data
