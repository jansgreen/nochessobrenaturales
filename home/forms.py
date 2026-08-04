from django import forms
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    TOPIC_CHOICES = (
        ("Confirmar asistencia", _("Quiero confirmar mi asistencia")),
        ("Petición de oración", _("Tengo una petición de oración")),
        ("Testimonio", _("Quiero compartir mi testimonio")),
        ("Biblia gratis", _("Quiero recibir una Biblia")),
        ("Servicio comunitario", _("Quiero servir a la comunidad")),
    )

    name = forms.CharField(
        label=_("Nombre completo"),
        max_length=120,
        validators=[
            MinLengthValidator(2, _("Escribe un nombre de al menos 2 caracteres."))
        ],
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        max_length=254,
        error_messages={"invalid": _("Ingresa un correo electrónico válido.")},
    )
    topic = forms.ChoiceField(
        label=_("¿Cómo podemos ayudarte?"),
        choices=TOPIC_CHOICES,
    )
    message = forms.CharField(
        label=_("Mensaje"),
        max_length=3000,
        validators=[
            MinLengthValidator(10, _("Escribe un mensaje de al menos 10 caracteres."))
        ],
        widget=forms.Textarea,
    )
    website = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.HiddenInput,
    )

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_message(self):
        return self.cleaned_data["message"].strip()
