from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import MinistryProfile, ShowcaseCategory, ShowcaseItem


MAX_PHOTO_SIZE = 8 * 1024 * 1024


class ShowcaseCategoryForm(forms.ModelForm):
    class Meta:
        model = ShowcaseCategory
        fields = (
            "title_es",
            "headline_es",
            "accent_es",
            "description_es",
            "title_en",
            "headline_en",
            "accent_en",
            "description_en",
            "title_pt",
            "headline_pt",
            "accent_pt",
            "description_pt",
            "position",
            "is_active",
        )
        labels = {
            "title_es": "Nombre de la categoría",
            "headline_es": "Título principal",
            "accent_es": "Segunda línea destacada",
            "description_es": "Introducción",
            "title_en": "Category name",
            "headline_en": "Main heading",
            "accent_en": "Highlighted second line",
            "description_en": "Introduction",
            "title_pt": "Nome da categoria",
            "headline_pt": "Título principal",
            "accent_pt": "Segunda linha em destaque",
            "description_pt": "Introdução",
            "position": "Posición de la fila",
            "is_active": "Mostrar esta fila en el home",
        }
        help_texts = {
            "accent_es": "Opcional. Aparecerá en cursiva debajo del título.",
            "description_en": "Optional. Spanish is used as a fallback.",
            "description_pt": "Opcional. O espanhol será usado como alternativa.",
            "position": "Los números menores aparecen primero.",
        }
        widgets = {
            "title_es": forms.TextInput(attrs={"placeholder": "Ej. Locaciones"}),
            "headline_es": forms.TextInput(
                attrs={"placeholder": "Ej. Un lugar para encontrarnos."}
            ),
            "accent_es": forms.TextInput(
                attrs={"placeholder": "Ej. Cerca de ti."}
            ),
            "description_es": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Presenta brevemente esta fila..."}
            ),
            "title_en": forms.TextInput(attrs={"placeholder": "E.g. Locations"}),
            "headline_en": forms.TextInput(
                attrs={"placeholder": "E.g. A place to gather."}
            ),
            "accent_en": forms.TextInput(attrs={"placeholder": "E.g. Near you."}),
            "description_en": forms.Textarea(attrs={"rows": 4}),
            "title_pt": forms.TextInput(attrs={"placeholder": "Ex. Localizações"}),
            "headline_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Um lugar para nos encontrarmos."}
            ),
            "accent_pt": forms.TextInput(attrs={"placeholder": "Ex. Perto de si."}),
            "description_pt": forms.Textarea(attrs={"rows": 4}),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("title", "headline", "accent", "description"):
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
        for field_name in ("title_es", "headline_es", "description_es"):
            self.fields[field_name].required = True
        for suffix in ("en", "pt"):
            for base_name in ("title", "headline", "accent", "description"):
                self.fields[f"{base_name}_{suffix}"].required = False


class ShowcaseItemForm(forms.ModelForm):
    class Meta:
        model = ShowcaseItem
        fields = (
            "category",
            "name",
            "role_es",
            "description_es",
            "alt_text_es",
            "role_en",
            "description_en",
            "alt_text_en",
            "role_pt",
            "description_pt",
            "alt_text_pt",
            "photo",
            "position",
            "is_active",
        )
        labels = {
            "category": "Categoría",
            "name": "Nombre de la persona o locación",
            "role_es": "Cargo, ciudad o detalle breve",
            "description_es": "Descripción breve",
            "alt_text_es": "Texto alternativo",
            "role_en": "Role, city, or short detail",
            "description_en": "Short description",
            "alt_text_en": "Alternative text",
            "role_pt": "Função, cidade ou detalhe breve",
            "description_pt": "Descrição breve",
            "alt_text_pt": "Texto alternativo",
            "photo": "Fotografía",
            "position": "Posición",
            "is_active": "Mostrar en el home",
        }
        help_texts = {
            "category": "Determina en cuál fila del home aparecerá la tarjeta.",
            "name": "Se mostrará igual en los tres idiomas.",
            "description_es": "Máximo 360 caracteres.",
            "description_en": "Optional. Spanish is used as a fallback.",
            "description_pt": "Opcional. O espanhol será usado como alternativa.",
            "alt_text_es": (
                "Describe brevemente la fotografía para personas que utilizan "
                "lectores de pantalla."
            ),
            "photo": "Formatos JPG, PNG o WebP. Tamaño máximo: 8 MB.",
            "position": "Los números menores aparecen primero.",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Ej. Pastor Richie Ramos o Washington Heights"}
            ),
            "role_es": forms.TextInput(
                attrs={"placeholder": "Ej. Conferencista internacional"}
            ),
            "description_es": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Presenta brevemente esta tarjeta..."}
            ),
            "alt_text_es": forms.TextInput(
                attrs={"placeholder": "Ej. Retrato del invitado o entrada de la locación"}
            ),
            "role_en": forms.TextInput(
                attrs={"placeholder": "E.g. International speaker"}
            ),
            "description_en": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Introduce this card briefly..."}
            ),
            "alt_text_en": forms.TextInput(
                attrs={"placeholder": "E.g. Guest portrait or location entrance"}
            ),
            "role_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Conferencista internacional"}
            ),
            "description_pt": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Apresente brevemente este cartão..."}
            ),
            "alt_text_pt": forms.TextInput(
                attrs={"placeholder": "Ex. Retrato do convidado ou entrada do local"}
            ),
            "photo": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("role", "description", "alt_text"):
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
        self.fields["description_es"].required = True
        self.fields["alt_text_es"].required = True
        for suffix in ("en", "pt"):
            self.fields[f"role_{suffix}"].required = False
            self.fields[f"description_{suffix}"].required = False
            self.fields[f"alt_text_{suffix}"].required = False

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError("La fotografía no puede superar los 8 MB.")
        return photo


class MinistryProfileForm(forms.ModelForm):
    class Meta:
        model = MinistryProfile
        fields = (
            "name",
            "profile_type",
            "role_es",
            "introduction_es",
            "biography_es",
            "alt_text_es",
            "role_en",
            "introduction_en",
            "biography_en",
            "alt_text_en",
            "role_pt",
            "introduction_pt",
            "biography_pt",
            "alt_text_pt",
            "photo",
            "position",
            "is_active",
        )
        labels = {
            "name": "Nombre completo",
            "profile_type": "Tipo de perfil",
            "role_es": "Cargo o ministerio",
            "introduction_es": "Presentación breve",
            "biography_es": "Biografía",
            "alt_text_es": "Texto alternativo de la fotografía",
            "role_en": "Role or ministry",
            "introduction_en": "Short introduction",
            "biography_en": "Biography",
            "alt_text_en": "Photo alternative text",
            "role_pt": "Cargo ou ministério",
            "introduction_pt": "Apresentação breve",
            "biography_pt": "Biografia",
            "alt_text_pt": "Texto alternativo da fotografia",
            "photo": "Fotografía principal",
            "position": "Posición",
            "is_active": "Mostrar en la página Nosotros",
        }
        help_texts = {
            "name": "Se mostrará igual en los tres idiomas.",
            "introduction_es": "Resumen editorial de hasta 500 caracteres.",
            "biography_es": "Puedes separar la biografía en varios párrafos.",
            "role_en": "Opcional. Si queda vacío, se mostrará el español.",
            "role_pt": "Opcional. Se ficar vazio, será apresentado o espanhol.",
            "photo": "Retrato vertical recomendado. JPG, PNG o WebP; máximo 8 MB.",
            "position": "Los números menores aparecen primero.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ej. Pastor Juan Pérez"}),
            "role_es": forms.TextInput(
                attrs={"placeholder": "Ej. Pastor invitado y conferencista"}
            ),
            "introduction_es": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Una presentación breve..."}
            ),
            "biography_es": forms.Textarea(
                attrs={"rows": 9, "placeholder": "Escribe aquí su historia y trayectoria..."}
            ),
            "alt_text_es": forms.TextInput(
                attrs={"placeholder": "Ej. Retrato del Pastor Juan Pérez"}
            ),
            "role_en": forms.TextInput(attrs={"placeholder": "E.g. Guest pastor"}),
            "introduction_en": forms.Textarea(attrs={"rows": 3}),
            "biography_en": forms.Textarea(attrs={"rows": 9}),
            "alt_text_en": forms.TextInput(attrs={"placeholder": "E.g. Portrait"}),
            "role_pt": forms.TextInput(attrs={"placeholder": "Ex. Pastor convidado"}),
            "introduction_pt": forms.Textarea(attrs={"rows": 3}),
            "biography_pt": forms.Textarea(attrs={"rows": 9}),
            "alt_text_pt": forms.TextInput(attrs={"placeholder": "Ex. Retrato"}),
            "photo": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("role", "introduction", "biography", "alt_text"):
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
        for field_name in (
            "role_es",
            "introduction_es",
            "biography_es",
            "alt_text_es",
        ):
            self.fields[field_name].required = True
        for suffix in ("en", "pt"):
            for base_name in ("role", "introduction", "biography", "alt_text"):
                self.fields[f"{base_name}_{suffix}"].required = False

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError("La fotografía no puede superar los 8 MB.")
        return photo
