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
            "eyebrow",
            "starts_at",
            "admission_text",
            "cta_text",
            "cta_url",
            "is_featured",
            "is_published",
        )
        labels = {
            "eyebrow": "Etiqueta superior",
            "admission_text": "Información de entrada",
            "cta_text": "Texto del botón",
            "cta_url": "Destino del botón",
            "is_featured": "Mostrar como próximo encuentro",
            "is_published": "Publicar en el calendario",
        }
        help_texts = {
            "eyebrow": "Ej. Próximo encuentro",
            "cta_url": "Ej. #contacto o /accounts/registro/",
            "is_featured": "Solo un evento puede ocupar la tarjeta principal.",
        }
        widgets = {
            "eyebrow": forms.TextInput(
                attrs={"placeholder": "Próximo encuentro"}
            ),
            "admission_text": forms.TextInput(
                attrs={"placeholder": "Entrada libre"}
            ),
            "cta_text": forms.TextInput(
                attrs={"placeholder": "Reservar mi lugar"}
            ),
            "cta_url": forms.TextInput(attrs={"placeholder": "#contacto"}),
        }

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
