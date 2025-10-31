from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import (
    BootstrapAuthenticationForm,
    StudentSignUpForm,
    TeacherSignUpForm,
)


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
