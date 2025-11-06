from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_classsession"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeacherAvailabilitySlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_time", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="availability_slots",
                        to="accounts.teacherprofile",
                    ),
                ),
            ],
            options={
                "ordering": ("start_time",),
                "verbose_name": "Horario disponible",
                "verbose_name_plural": "Horarios disponibles",
            },
        ),
        migrations.AddConstraint(
            model_name="teacheravailabilityslot",
            constraint=models.UniqueConstraint(
                fields=("teacher", "start_time"),
                name="unique_teacher_slot_start_time",
            ),
        ),
        migrations.AddField(
            model_name="classsession",
            name="slot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="class_sessions",
                to="accounts.teacheravailabilityslot",
            ),
        ),
        migrations.AddConstraint(
            model_name="classsession",
            constraint=models.UniqueConstraint(
                condition=models.Q(status="scheduled"),
                fields=("slot",),
                name="unique_scheduled_slot",
            ),
        ),
    ]
