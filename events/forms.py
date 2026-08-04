from django import forms
from django.db import transaction
from django.utils import timezone

from .models import Event, YouTubeVideo, extract_youtube_video_id


class EventForm(forms.ModelForm):
    starts_at = forms.DateTimeField(
        label="Fecha y hora",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )

    class Meta:
        model = Event
        fields = (
            "eyebrow_es",
            "admission_text_es",
            "cta_text_es",
            "eyebrow_en",
            "admission_text_en",
            "cta_text_en",
            "eyebrow_pt",
            "admission_text_pt",
            "cta_text_pt",
            "starts_at",
            "cta_url",
            "is_featured",
            "is_published",
        )
        labels = {
            "eyebrow_es": "Etiqueta superior",
            "admission_text_es": "Información de entrada",
            "cta_text_es": "Texto del botón",
            "eyebrow_en": "Top label",
            "admission_text_en": "Admission information",
            "cta_text_en": "Button text",
            "eyebrow_pt": "Etiqueta superior",
            "admission_text_pt": "Informação de entrada",
            "cta_text_pt": "Texto do botão",
            "cta_url": "Destino del botón",
            "is_featured": "Mostrar como próximo encuentro",
            "is_published": "Publicar en el calendario",
        }
        help_texts = {
            "eyebrow_es": "Ej. Próximo encuentro",
            "eyebrow_en": "E.g. Next gathering",
            "eyebrow_pt": "Ex. Próximo encontro",
            "cta_url": "Ej. #contacto o /accounts/registro/",
            "is_featured": "Solo un evento puede ocupar la tarjeta principal.",
        }
        widgets = {
            "eyebrow_es": forms.TextInput(
                attrs={"placeholder": "Próximo encuentro"}
            ),
            "admission_text_es": forms.TextInput(
                attrs={"placeholder": "Entrada libre"}
            ),
            "cta_text_es": forms.TextInput(
                attrs={"placeholder": "Reservar mi lugar"}
            ),
            "eyebrow_en": forms.TextInput(
                attrs={"placeholder": "Next gathering"}
            ),
            "admission_text_en": forms.TextInput(
                attrs={"placeholder": "Free admission"}
            ),
            "cta_text_en": forms.TextInput(
                attrs={"placeholder": "Reserve my place"}
            ),
            "eyebrow_pt": forms.TextInput(
                attrs={"placeholder": "Próximo encontro"}
            ),
            "admission_text_pt": forms.TextInput(
                attrs={"placeholder": "Entrada gratuita"}
            ),
            "cta_text_pt": forms.TextInput(
                attrs={"placeholder": "Reservar o meu lugar"}
            ),
            "cta_url": forms.TextInput(attrs={"placeholder": "#contacto"}),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data", args[0] if args else None)
        if data is not None:
            data = data.copy()
            for base_name in ("eyebrow", "admission_text", "cta_text"):
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
            "eyebrow_es",
            "admission_text_es",
            "cta_text_es",
            "eyebrow_en",
            "admission_text_en",
            "cta_text_en",
            "eyebrow_pt",
            "admission_text_pt",
            "cta_text_pt",
        ):
            self.fields[field_name].required = True

    def clean_starts_at(self):
        starts_at = self.cleaned_data["starts_at"]
        if starts_at <= timezone.now():
            raise forms.ValidationError(
                "Selecciona una fecha y hora futuras."
            )
        return starts_at

    @transaction.atomic
    def save(self, commit=True):
        event = super().save(commit=False)
        if event.is_featured:
            Event.objects.exclude(pk=event.pk).update(is_featured=False)
        if commit:
            event.save()
            self.save_m2m()
        return event


class YouTubeVideoForm(forms.ModelForm):
    class Meta:
        model = YouTubeVideo
        fields = (
            "youtube_url",
            "position",
            "show_on_home",
            "is_active",
        )
        labels = {
            "youtube_url": "Enlace del video",
            "position": "Posición",
            "show_on_home": "Destacar también en el inicio",
            "is_active": "Mostrar en la galería pública",
        }
        help_texts = {
            "youtube_url": (
                "Acepta youtube.com, youtu.be, Shorts y transmisiones "
                "guardadas. El título y la miniatura se completan solos."
            ),
            "position": "Los números menores aparecen primero.",
            "show_on_home": (
                "El inicio muestra como máximo los primeros tres videos."
            ),
        }
        widgets = {
            "youtube_url": forms.URLInput(
                attrs={
                    "placeholder": "https://www.youtube.com/watch?v=...",
                    "autocomplete": "off",
                    "spellcheck": "false",
                }
            ),
            "position": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_youtube_url(self):
        youtube_url = self.cleaned_data["youtube_url"]
        youtube_id = extract_youtube_video_id(youtube_url)
        duplicates = YouTubeVideo.objects.filter(youtube_id=youtube_id)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError(
                "Este video ya fue agregado a la galería."
            )

        return f"https://www.youtube.com/watch?v={youtube_id}"
