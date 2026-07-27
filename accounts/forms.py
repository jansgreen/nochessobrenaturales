from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "tu@email.com",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "Nombre de usuario"}
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "autocomplete": "username",
                    "autofocus": True,
                    "placeholder": "Elige un nombre de usuario",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = (
            "Usa hasta 150 caracteres: letras, números y @/./+/-/_."
        )
        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].help_text = (
            "Debe tener al menos 8 caracteres y no ser demasiado común."
        )
        self.fields["password1"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Crea una contraseña segura",
            }
        )
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].help_text = "Escribe la misma contraseña nuevamente."
        self.fields["password2"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Repite tu contraseña",
            }
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Tu nombre de usuario",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Tu contraseña",
            }
        ),
    )

    error_messages = {
        "invalid_login": (
            "El nombre de usuario o la contraseña no son correctos. "
            "Verifica los datos e inténtalo nuevamente."
        ),
        "inactive": "Esta cuenta está inactiva.",
    }

