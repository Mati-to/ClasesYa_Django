import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
    class Availability(models.TextChoices):
        MORNING = "morning", _("Manana")
        AFTERNOON = "afternoon", _("Tarde")
        EVENING = "evening", _("Noche")
        WEEKEND = "weekend", _("Fin de semana")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    subjects = models.CharField(max_length=150)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    bio = models.TextField(blank=True)
    availability = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"Profesor: {self.user.get_full_name() or self.user.username}"

    def availability_labels(self) -> list[str]:
        if not self.availability:
            return []
        display_map = dict(self.Availability.choices)
        return [display_map.get(option, option) for option in self.availability]


class ClassSession(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Programada")
        COMPLETED = "completed", _("Completada")
        CANCELLED = "cancelled", _("Cancelada")

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="class_sessions",
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="class_sessions",
    )
    topic = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    virtual_room_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ("-start_time",)
        verbose_name = _("Sesion en linea")
        verbose_name_plural = _("Sesiones en linea")
        constraints = [
            models.UniqueConstraint(
                fields=("teacher", "student", "start_time", "end_time"),
                name="unique_session_teacher_student_time",
            )
        ]

    def __str__(self) -> str:
        return (
            f"Sesion {self.topic} - "
            f"{self.teacher.user.get_full_name() or self.teacher.user.username} / "
            f"{self.student.user.get_full_name() or self.student.user.username}"
        )

    def clean(self):
        super().clean()
        if not self.teacher_id or not self.student_id:
            return
        if self.start_time >= self.end_time:
            raise ValidationError({"end_time": _("La hora de finalizacion debe ser posterior al inicio.")})

        if self.start_time < timezone.now() - timedelta(minutes=1):
            raise ValidationError({"start_time": _("La hora de inicio debe ser en el futuro.")})

        overlapping_filter = models.Q(status=self.Status.SCHEDULED)
        overlapping_filter &= (
            models.Q(start_time__lt=self.end_time) & models.Q(end_time__gt=self.start_time)
        )

        teacher_overlap_qs = ClassSession.objects.filter(teacher=self.teacher).filter(overlapping_filter)
        student_overlap_qs = ClassSession.objects.filter(student=self.student).filter(overlapping_filter)

        if self.pk:
            teacher_overlap_qs = teacher_overlap_qs.exclude(pk=self.pk)
            student_overlap_qs = student_overlap_qs.exclude(pk=self.pk)

        if teacher_overlap_qs.exists():
            raise ValidationError(
                {
                    "teacher": _(
                        "El profesor ya tiene una sesion programada en ese horario. Por favor elige otro horario."
                    )
                }
            )

        if student_overlap_qs.exists():
            raise ValidationError(
                {
                    "student": _(
                        "El estudiante ya tiene una sesion programada en ese horario. Por favor elige otro horario."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def virtual_room_url(self) -> str:
        return f"https://meet.jit.si/ClasesYa-{self.virtual_room_code}"

    def is_scheduled(self) -> bool:
        return self.status == self.Status.SCHEDULED

    def has_finished(self) -> bool:
        return timezone.now() >= self.end_time
