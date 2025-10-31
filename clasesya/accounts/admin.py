from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Rol en ClasesYa",
            {"fields": ("user_type",)},
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_staff",
    )
    list_filter = DjangoUserAdmin.list_filter + ("user_type",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "preferred_subject")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "preferred_subject",
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "subjects", "hourly_rate")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "subjects",
    )
