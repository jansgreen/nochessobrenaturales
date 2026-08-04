from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import GalleryImage


MAX_IMAGE_SIZE = 8 * 1024 * 1024


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = (
            "title_es",
            "description_es",
            "alt_text_es",
            "title_en",
            "description_en",
            "alt_text_en",
            "title_pt",
            "description_pt",
            "alt_text_pt",
            "image",
            "photographed_on",
            "position",
            "is_active",
        )
        labels = {
            "title_es": "Título",
            "description_es": "Descripción",
            "alt_text_es": "Texto alternativo",
            "title_en": "Title",
            "description_en": "Description",
            "alt_text_en": "Alternative text",
            "title_pt": "Título",
            "description_pt": "Descrição",
            "alt_text_pt": "Texto alternativo",
            "image": "Imagen",
            "alt_text": "Texto alternativo",
            "photographed_on": "Fecha de la fotografía",
            "position": "Posición",
            "is_active": "Mostrar en la galería pública",
        }
        help_texts = {
            "description_es": "Texto opcional que aparecerá en el visor ampliado.",
            "description_en": "Optional text displayed in the expanded viewer.",
            "description_pt": "Texto opcional apresentado no visualizador ampliado.",
            "image": "Formatos JPG, PNG o WebP. Tamaño máximo: 8 MB.",
            "alt_text_es": (
                "Describe brevemente lo que aparece en la imagen para "
                "personas que utilizan lectores de pantalla."
            ),
            "alt_text_en": "Briefly describe the image for screen-reader users.",
            "alt_text_pt": "Descreva brevemente a imagem para utilizadores de leitores de ecrã.",
            "photographed_on": "Opcional. Se mostrará como parte del recuerdo.",
            "position": "Los números menores aparecen primero.",
        }
        widgets = {
            "title_es": forms.TextInput(
                attrs={"placeholder": "Ej. Una noche de adoración"}
            ),
            "description_es": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Cuenta brevemente este momento..."}
            ),
            "alt_text_es": forms.TextInput(
                attrs={"placeholder": "Ej. Congregación durante la adoración"}
            ),
            "title_en": forms.TextInput(
                attrs={"placeholder": "E.g. A night of worship"}
            ),
            "description_en": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell the story of this moment..."}
            ),
            "alt_text_en": forms.TextInput(
                attrs={"placeholder": "E.g. Congregation during worship"}
            ),
            "title_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Uma noite de adoração"}
            ),
            "description_pt": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Conte brevemente este momento..."}
            ),
            "alt_text_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Congregação durante a adoração"}
            ),
            "image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
            "photographed_on": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("title", "description", "alt_text"):
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
            self.fields[f"alt_text_{suffix}"].required = True

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if isinstance(image, UploadedFile) and image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError(
                "La imagen no puede superar los 8 MB."
            )
        return image
