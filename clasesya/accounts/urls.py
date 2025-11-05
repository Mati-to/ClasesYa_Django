from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    HomeView,
    LandingPageView,
    ProfileUpdateView,
    StudentSignUpView,
    TeacherSignUpView,
    TeacherSearchView,
    TeacherProfileDetailView,
)


app_name = "accounts"


urlpatterns = [
    path("", LandingPageView.as_view(), name="landing"),
    path("home/", HomeView.as_view(), name="home"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("perfil/", ProfileUpdateView.as_view(), name="profile_update"),
    path("profesores/", TeacherSearchView.as_view(), name="teacher_search"),
    path("profesores/<int:pk>/", TeacherProfileDetailView.as_view(), name="teacher_detail"),
    path("registro/alumno/", StudentSignUpView.as_view(), name="student_signup"),
    path("registro/profesor/", TeacherSignUpView.as_view(), name="teacher_signup"),
]
