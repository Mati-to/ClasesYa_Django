from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class UserType(models.TextChoices):
        STUDENT = "STUDENT", _("Student")
        TEACHER = "TEACHER", _("Teacher")

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STUDENT,
    )

    def is_student(self) -> bool:
        return self.user_type == self.UserType.STUDENT

    def is_teacher(self) -> bool:
        return self.user_type == self.UserType.TEACHER


class StudentProfile(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    preferred_subject = models.CharField(max_length=100, blank=True)
    learning_goals = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Perfil estudiante: {self.user.get_full_name() or self.user.username}"


class TeacherProfile(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    subjects = models.CharField(max_length=150)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Profesor: {self.user.get_full_name() or self.user.username}"
