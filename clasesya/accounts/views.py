from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, TemplateView

from .forms import (
    BootstrapAuthenticationForm,
    StudentSignUpForm,
    StudentProfileUpdateForm,
    TeacherSignUpForm,
    TeacherProfileUpdateForm,
    TeacherSearchForm,
    UserAccountUpdateForm,
    ClassSessionScheduleForm,
    ClassSessionStatusForm,
)
from .models import ClassSession, StudentProfile, TeacherProfile


class LandingPageView(TemplateView):
    template_name = "landing.html"


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = reverse_lazy("accounts:login")


class StudentSignUpView(CreateView):
    form_class = StudentSignUpForm
    template_name = "accounts/student_signup.html"
    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class TeacherSignUpView(CreateView):
    form_class = TeacherSignUpForm
    template_name = "accounts/teacher_signup.html"
    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    authentication_form = BootstrapAuthenticationForm
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse_lazy("accounts:home")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:landing")


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_update.html"
    login_url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        context = self._build_context()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self._build_context(data=request.POST)
        user_form = context["user_form"]
        profile_form = context.get("profile_form")

        forms_valid = user_form.is_valid()
        if profile_form is not None:
            forms_valid = forms_valid and profile_form.is_valid()

        if forms_valid:
            user_form.save()
            if profile_form is not None:
                profile_form.save()
            messages.success(request, "Tu perfil se actualizo correctamente.")
            return redirect("accounts:home")

        return self.render_to_response(context)

    def _build_context(self, data=None):
        user = self.request.user
        user_form = UserAccountUpdateForm(data=data, instance=user)

        profile_form = None
        profile_title = None

        if user.is_student():
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            profile_form = StudentProfileUpdateForm(data=data, instance=profile)
            profile_title = "Preferencias de estudio"
        elif user.is_teacher():
            profile, _ = TeacherProfile.objects.get_or_create(user=user)
            profile_form = TeacherProfileUpdateForm(data=data, instance=profile)
            profile_title = "Perfil docente"

        return {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile_title": profile_title,
            "is_student": user.is_student(),
            "is_teacher": user.is_teacher(),
        }


class TeacherSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/teacher_search.html"
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_student():
            messages.info(request, "Solo los alumnos pueden buscar profesores.")
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TeacherSearchForm(self.request.GET or None)
        teachers_queryset = (
            TeacherProfile.objects.select_related("user")
            .order_by("user__first_name", "user__last_name")
        )
        applied_filters = False

        if form.is_valid():
            subject = form.cleaned_data.get("subject")
            availability = form.cleaned_data.get("availability")

            if subject:
                teachers_queryset = teachers_queryset.filter(subjects__icontains=subject)
                applied_filters = True

            teachers = list(teachers_queryset)

            if availability:
                teachers = [
                    teacher
                    for teacher in teachers
                    if all(slot in (teacher.availability or []) for slot in availability)
                ]
                applied_filters = True
        else:
            form = TeacherSearchForm()
            teachers = list(teachers_queryset)

        total_results = len(teachers)

        context.update(
            {
                "form": form,
                "teachers": teachers,
                "applied_filters": applied_filters,
                "total_results": total_results,
            }
        )
        return context


class TeacherProfileDetailView(LoginRequiredMixin, DetailView):
    model = TeacherProfile
    template_name = "accounts/teacher_detail.html"
    context_object_name = "teacher"
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_student():
            messages.info(request, "Solo los alumnos pueden consultar perfiles de profesores.")
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        teacher_name = self.object.user.get_full_name() or self.object.user.username
        messages.success(
            request,
            f"Has seleccionado a {teacher_name}. Te enviaremos los siguientes pasos a tu correo.",
        )
        return redirect("accounts:teacher_detail", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["availability_labels"] = self.object.availability_labels()
        return context


class ClassSessionCreateView(LoginRequiredMixin, FormView):
    template_name = "accounts/class_session_form.html"
    form_class = ClassSessionScheduleForm
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_student():
            messages.info(request, "Solo los alumnos pueden programar sesiones en linea.")
            return redirect("accounts:home")
        self.teacher_profile = get_object_or_404(
            TeacherProfile.objects.select_related("user"), pk=kwargs["teacher_pk"]
        )
        self.student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        self._form_error_reported = False
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.teacher_profile
        kwargs["student"] = self.student_profile
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "teacher": self.teacher_profile,
            }
        )
        return context

    def form_valid(self, form):
        try:
            session = form.save()
        except ValidationError as exc:
            for field, errors in exc.message_dict.items():
                target_field = field if field in form.fields else None
                for error in errors:
                    form.add_error(target_field, error)
            messages.error(
                self.request,
                "No pudimos programar la sesion por conflictos con la agenda. Revisa los horarios seleccionados.",
            )
            self._form_error_reported = True
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Tu clase se programo correctamente. Puedes acceder a los detalles desde tus sesiones.",
        )
        return redirect("accounts:session_detail", pk=session.pk)

    def form_invalid(self, form):
        if not getattr(self, "_form_error_reported", False):
            messages.error(self.request, "Revisa la informacion ingresada. No se pudo programar la sesion.")
        return super().form_invalid(form)


class ClassSessionListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/class_session_list.html"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        user = self.request.user
        base_qs = ClassSession.objects.select_related("teacher__user", "student__user")
        if user.is_student():
            return base_qs.filter(student__user=user)
        if user.is_teacher():
            return base_qs.filter(teacher__user=user)
        return base_qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        sessions_qs = self.get_queryset()
        upcoming_sessions = sessions_qs.filter(
            status=ClassSession.Status.SCHEDULED,
            start_time__gte=now,
        ).order_by("start_time")
        past_sessions = sessions_qs.exclude(
            Q(status=ClassSession.Status.SCHEDULED) & Q(start_time__gte=now)
        ).order_by("-start_time")
        context.update(
            {
                "upcoming_sessions": upcoming_sessions,
                "past_sessions": past_sessions,
                "is_student": self.request.user.is_student(),
                "is_teacher": self.request.user.is_teacher(),
            }
        )
        return context


class ClassSessionDetailView(LoginRequiredMixin, DetailView):
    model = ClassSession
    template_name = "accounts/class_session_detail.html"
    context_object_name = "session"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        base_qs = super().get_queryset().select_related("teacher__user", "student__user")
        user = self.request.user
        if user.is_student():
            return base_qs.filter(student__user=user)
        if user.is_teacher():
            return base_qs.filter(teacher__user=user)
        return base_qs.none()

    def _user_can_manage_status(self) -> bool:
        return self.request.user.is_teacher() and self.object.teacher.user_id == self.request.user.id

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self._user_can_manage_status():
            messages.error(request, "No tienes permisos para modificar esta sesion.")
            return redirect("accounts:session_detail", pk=self.object.pk)

        form = ClassSessionStatusForm(data=request.POST, instance=self.object)
        if form.is_valid():
            updated_session = form.save()
            status_label = updated_session.get_status_display()
            messages.success(request, f"El estado de la sesion se actualizo a '{status_label}'.")
            return redirect("accounts:session_detail", pk=updated_session.pk)

        context = self.get_context_data(status_form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        can_manage_status = self.request.user.is_teacher() and session.teacher.user_id == self.request.user.id
        status_form = kwargs.get("status_form")
        if status_form is None and can_manage_status:
            status_form = ClassSessionStatusForm(instance=session)
        context.update(
            {
                "status_form": status_form,
                "can_manage_status": can_manage_status,
                "can_join_room": session.status == ClassSession.Status.SCHEDULED,
                "start_time_local": timezone.localtime(session.start_time),
                "end_time_local": timezone.localtime(session.end_time),
            }
        )
        return context


class ClassSessionRoomView(LoginRequiredMixin, DetailView):
    model = ClassSession
    template_name = "accounts/class_session_room.html"
    context_object_name = "session"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        base_qs = super().get_queryset().select_related("teacher__user", "student__user")
        user = self.request.user
        if user.is_student():
            return base_qs.filter(student__user=user)
        if user.is_teacher():
            return base_qs.filter(teacher__user=user)
        return base_qs.none()

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        session = self.object
        if session.status == ClassSession.Status.CANCELLED:
            messages.error(request, "Esta sesion fue cancelada. No es posible acceder a la sala virtual.")
            return redirect("accounts:session_detail", pk=session.pk)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        parsed_url = urlparse(session.virtual_room_url)
        room_name = parsed_url.path.strip("/")
        context.update(
            {
                "room_domain": parsed_url.netloc,
                "room_name": room_name,
                "start_time_local": timezone.localtime(session.start_time),
                "end_time_local": timezone.localtime(session.end_time),
                "is_in_future": session.start_time > timezone.now(),
            }
        )
        return context
