from django import forms
from django.core.validators import MinLengthValidator


class ContactForm(forms.Form):
    TOPIC_CHOICES = (
        ("Confirmar asistencia", "Quiero confirmar mi asistencia"),
        ("Petición de oración", "Tengo una petición de oración"),
        ("Testimonio", "Quiero compartir mi testimonio"),
        ("Biblia gratis", "Quiero recibir una Biblia"),
        ("Servicio comunitario", "Quiero servir a la comunidad"),
    )

    name = forms.CharField(
        label="Nombre completo",
        max_length=120,
        validators=[
            MinLengthValidator(2, "Escribe un nombre de al menos 2 caracteres.")
        ],
    )
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        error_messages={"invalid": "Ingresa un correo electrónico válido."},
    )
    topic = forms.ChoiceField(
        label="¿Cómo podemos ayudarte?",
        choices=TOPIC_CHOICES,
    )
    message = forms.CharField(
        label="Mensaje",
        max_length=3000,
        validators=[
            MinLengthValidator(10, "Escribe un mensaje de al menos 10 caracteres.")
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

