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
    availability = forms.MultipleChoiceField(
        choices=TeacherProfile.Availability.choices,
        label="Disponibilidad",
        required=False,
        help_text="Selecciona los momentos en los que puedes dictar clases",
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["availability"].widget.attrs["class"] = "form-select"

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
                availability=self.cleaned_data.get("availability", []),
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


class UserAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electronico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_classes} form-control".strip()
        self.fields["first_name"].widget.attrs.setdefault("placeholder", "Nombre")
        self.fields["last_name"].widget.attrs.setdefault("placeholder", "Apellido")
        self.fields["email"].widget.attrs.setdefault("placeholder", "correo@ejemplo.com")


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("preferred_subject", "learning_goals")
        labels = {
            "preferred_subject": "Asignatura de interes",
            "learning_goals": "Objetivos de aprendizaje",
        }
        widgets = {
            "learning_goals": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_classes} form-control".strip()
        self.fields["preferred_subject"].widget.attrs.setdefault("placeholder", "Materia principal")
        self.fields["learning_goals"].widget.attrs.setdefault(
            "placeholder",
            "Cuentanos que deseas alcanzar",
        )


class TeacherProfileUpdateForm(forms.ModelForm):
    availability = forms.MultipleChoiceField(
        choices=TeacherProfile.Availability.choices,
        label="Disponibilidad",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        help_text="Indica cuando estas disponible para recibir nuevos alumnos",
    )

    class Meta:
        model = TeacherProfile
        fields = ("subjects", "hourly_rate", "bio", "availability")
        labels = {
            "subjects": "Asignaturas",
            "hourly_rate": "Tarifa por hora (USD)",
            "bio": "Biografia",
            "availability": "Disponibilidad",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_classes = field.widget.attrs.get("class", "")
            if name == "availability":
                field.widget.attrs["class"] = f"{css_classes} form-select".strip()
            else:
                field.widget.attrs["class"] = f"{css_classes} form-control".strip()
        self.fields["subjects"].widget.attrs.setdefault(
            "placeholder",
            "Ej: Algebra, Fisica, Programacion",
        )
        self.fields["hourly_rate"].widget.attrs.setdefault("min", "0")
        self.fields["bio"].widget.attrs.setdefault(
            "placeholder",
            "Describe tu experiencia docente",
        )
        if self.instance and self.instance.pk:
            self.fields["availability"].initial = self.instance.availability

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.availability = self.cleaned_data.get("availability", [])
        if commit:
            profile.save()
        return profile


class TeacherSearchForm(forms.Form):
    subject = forms.CharField(
        label="Area de interes",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej: Algebra, Programacion",
            }
        ),
    )
    availability = forms.MultipleChoiceField(
        choices=TeacherProfile.Availability.choices,
        label="Disponibilidad",
        required=False,
        widget=forms.SelectMultiple(),
        help_text="Puedes seleccionar uno o varios horarios",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].widget.attrs["class"] = "form-control"
        self.fields["availability"].widget.attrs["class"] = "form-select"
