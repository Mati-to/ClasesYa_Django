from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView

from .forms import (
    BootstrapAuthenticationForm,
    StudentSignUpForm,
    StudentProfileUpdateForm,
    TeacherSignUpForm,
    TeacherProfileUpdateForm,
    TeacherSearchForm,
    UserAccountUpdateForm,
)
from .models import StudentProfile, TeacherProfile


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
