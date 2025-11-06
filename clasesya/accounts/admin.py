from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import (
    ClassSession,
    StudentProfile,
    TeacherAvailabilitySlot,
    TeacherProfile,
    User,
)


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


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "topic",
        "teacher",
        "student",
        "start_time",
        "end_time",
        "status",
        "virtual_room_link",
    )
    autocomplete_fields = ("teacher", "student")
    search_fields = (
        "topic",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "student__user__first_name",
        "student__user__last_name",
    )
    list_filter = ("status", "start_time")
    readonly_fields = (
        "created_at",
        "updated_at",
        "virtual_room_code",
        "virtual_room_preview",
    )

    def virtual_room_link(self, obj):
        return format_html('<a href="{}" target="_blank">Abrir sala</a>', obj.virtual_room_url)

    virtual_room_link.short_description = "Sala virtual"

    def virtual_room_preview(self, obj):
        return obj.virtual_room_url

    virtual_room_preview.short_description = "Enlace de la sala"


@admin.register(TeacherAvailabilitySlot)
class TeacherAvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("teacher", "start_time", "is_active", "is_slot_available")
    list_filter = ("is_active",)
    search_fields = (
        "teacher__user__first_name",
        "teacher__user__last_name",
        "teacher__user__username",
    )
    autocomplete_fields = ("teacher",)
    ordering = ("start_time",)

    def is_slot_available(self, obj):
        return obj.is_available()

    is_slot_available.boolean = True
    is_slot_available.short_description = "Disponible"
