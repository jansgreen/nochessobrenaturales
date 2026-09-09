from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm


User = get_user_model()


ACCESS_MEMBER = "member"
ACCESS_STAFF = "staff"
ACCESS_SUPERUSER = "superuser"
ACCESS_LEVEL_CHOICES = (
    (ACCESS_MEMBER, "Miembro · solo consulta su panel"),
    (ACCESS_STAFF, "Personal · administra el contenido"),
    (ACCESS_SUPERUSER, "Superusuario · administra contenido y usuarios"),
)


class UserAccessMixin:
    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.is_superuser:
                level = ACCESS_SUPERUSER
            elif self.instance.is_staff:
                level = ACCESS_STAFF
            else:
                level = ACCESS_MEMBER
            self.fields["access_level"].initial = level

        for field_name in ("username", "first_name", "last_name", "email"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.setdefault("autocomplete", field_name)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            return email
        existing = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance or not self.instance.pk:
            return cleaned_data

        access_level = cleaned_data.get("access_level")
        is_active = cleaned_data.get("is_active")
        if self.actor and self.actor.pk == self.instance.pk:
            if access_level != ACCESS_SUPERUSER:
                self.add_error(
                    "access_level",
                    "No puedes reducir tu propio nivel de acceso.",
                )
            if not is_active:
                self.add_error("is_active", "No puedes desactivar tu propia cuenta.")

        if (
            self.instance.is_superuser
            and access_level != ACCESS_SUPERUSER
            and User.objects.filter(is_superuser=True).count() <= 1
        ):
            self.add_error(
                "access_level",
                "Debe permanecer al menos un superusuario activo.",
            )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        level = self.cleaned_data["access_level"]
        user.is_staff = level in (ACCESS_STAFF, ACCESS_SUPERUSER)
        user.is_superuser = level == ACCESS_SUPERUSER
        if commit:
            user.save()
        return user


class DashboardUserCreationForm(UserAccessMixin, UserCreationForm):
    access_level = forms.ChoiceField(
        label="Nivel de acceso",
        choices=ACCESS_LEVEL_CHOICES,
        help_text="Los permisos del dashboard se asignan automáticamente.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "access_level",
            "is_active",
            "password1",
            "password2",
        )
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Cuenta activa",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Ej. maria.rivera"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["is_active"].initial = True
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"


class DashboardUserUpdateForm(UserAccessMixin, forms.ModelForm):
    access_level = forms.ChoiceField(
        label="Nivel de acceso",
        choices=ACCESS_LEVEL_CHOICES,
        help_text="Los permisos del dashboard se asignan automáticamente.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "access_level",
            "is_active",
        )
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Cuenta activa",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Ej. maria.rivera"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False


class DashboardSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password2"].label = "Confirmar nueva contraseña"
        self.fields["new_password1"].widget.attrs.update(
            {"autocomplete": "new-password", "placeholder": "Nueva contraseña"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"autocomplete": "new-password", "placeholder": "Repite la contraseña"}
        )
