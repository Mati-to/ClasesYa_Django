from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import StudentProfile, TeacherProfile, User


class BaseSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Nombre", required=True)
    last_name = forms.CharField(max_length=150, label="Apellido", required=True)
    email = forms.EmailField(label="Correo electronico", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_classes} form-control".strip()
        self.fields["username"].widget.attrs.setdefault("placeholder", "Nombre de usuario")
        self.fields["first_name"].widget.attrs.setdefault("placeholder", "Nombre")
        self.fields["last_name"].widget.attrs.setdefault("placeholder", "Apellido")
        self.fields["email"].widget.attrs.setdefault("placeholder", "correo@ejemplo.com")

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class StudentSignUpForm(BaseSignUpForm):
    preferred_subject = forms.CharField(
        max_length=100,
        label="Asignatura de interes",
        required=False,
        help_text="Materia que te gustaria reforzar",
    )
    learning_goals = forms.CharField(
        label="Objetivos de aprendizaje",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.user_type = User.UserType.STUDENT
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                preferred_subject=self.cleaned_data.get("preferred_subject", ""),
                learning_goals=self.cleaned_data.get("learning_goals", ""),
            )
        return user


class TeacherSignUpForm(BaseSignUpForm):
    subjects = forms.CharField(
        max_length=150,
        label="Asignaturas que impartes",
        help_text="Ej: Algebra, Fisica, Programacion",
    )
    hourly_rate = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=0,
        label="Tarifa por hora (USD)",
    )
    bio = forms.CharField(
        label="Biografia",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.user_type = User.UserType.TEACHER
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                subjects=self.cleaned_data.get("subjects", ""),
                hourly_rate=self.cleaned_data.get("hourly_rate"),
                bio=self.cleaned_data.get("bio", ""),
            )
        return user


class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Usuario"}),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contrasena"}),
    )
