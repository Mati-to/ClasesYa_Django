from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import StudentProfile, TeacherProfile


class LogoutFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_logout_via_post_redirects_to_landing_and_clears_session(self):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:landing"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_profile_update_requires_authentication(self):
        response = self.client.get(reverse("accounts:profile_update"))
        expected_redirect = f"{reverse('accounts:login')}?next={reverse('accounts:profile_update')}"
        self.assertRedirects(response, expected_redirect)

    def test_student_can_update_profile(self):
        user = self.user_model.objects.create_user(
            username="student1",
            password="pass1234",
            first_name="Ana",
            last_name="Lopez",
            email="ana@example.com",
        )
        user.user_type = user.UserType.STUDENT
        user.save()
        StudentProfile.objects.create(
            user=user,
            preferred_subject="Matematicas",
            learning_goals="Mejorar algebra",
        )

        self.client.login(username="student1", password="pass1234")

        response = self.client.post(
            reverse("accounts:profile_update"),
            {
                "first_name": "Ana Maria",
                "last_name": "Lopez",
                "email": "ana.maria@example.com",
                "preferred_subject": "Historia",
                "learning_goals": "Aprender historia universal",
            },
        )

        self.assertRedirects(response, reverse("accounts:home"))

        user.refresh_from_db()
        student_profile = user.student_profile
        self.assertEqual(user.first_name, "Ana Maria")
        self.assertEqual(user.email, "ana.maria@example.com")
        self.assertEqual(student_profile.preferred_subject, "Historia")
        self.assertEqual(student_profile.learning_goals, "Aprender historia universal")

    def test_teacher_can_update_profile(self):
        user = self.user_model.objects.create_user(
            username="teacher1",
            password="pass1234",
            first_name="Luis",
            last_name="Gomez",
            email="luis@example.com",
        )
        user.user_type = user.UserType.TEACHER
        user.save()
        TeacherProfile.objects.create(
            user=user,
            subjects="Fisica",
            hourly_rate=Decimal("25.00"),
            bio="Profesor experimentado",
        )

        self.client.login(username="teacher1", password="pass1234")

        response = self.client.post(
            reverse("accounts:profile_update"),
            {
                "first_name": "Luis Alberto",
                "last_name": "Gomez",
                "email": "lgomez@example.com",
                "subjects": "Fisica, Matematicas",
                "hourly_rate": "30.50",
                "bio": "Amante de la experimentacion",
            },
        )

        self.assertRedirects(response, reverse("accounts:home"))

        user.refresh_from_db()
        teacher_profile = user.teacher_profile
        self.assertEqual(user.first_name, "Luis Alberto")
        self.assertEqual(user.email, "lgomez@example.com")
        self.assertEqual(teacher_profile.subjects, "Fisica, Matematicas")
        self.assertEqual(teacher_profile.hourly_rate, Decimal("30.50"))
        self.assertEqual(teacher_profile.bio, "Amante de la experimentacion")


class TeacherSearchViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

        self.student = self.user_model.objects.create_user(
            username="alumna",
            password="pass1234",
            first_name="Ana",
            last_name="Perez",
            email="ana@student.com",
        )
        self.student.user_type = self.student.UserType.STUDENT
        self.student.save()

        self.teacher_user = self.user_model.objects.create_user(
            username="profe1",
            password="pass1234",
            first_name="Luis",
            last_name="Gomez",
            email="luis@teacher.com",
        )
        self.teacher_user.user_type = self.teacher_user.UserType.TEACHER
        self.teacher_user.save()

        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            subjects="Fisica avanzada",
            hourly_rate=Decimal("40.00"),
            bio="Apasionado por la ciencia",
            availability=[
                TeacherProfile.Availability.MORNING,
                TeacherProfile.Availability.WEEKEND,
            ],
        )

        other_teacher_user = self.user_model.objects.create_user(
            username="profe2",
            password="pass1234",
            first_name="Maria",
            last_name="Lopez",
            email="maria@teacher.com",
        )
        other_teacher_user.user_type = other_teacher_user.UserType.TEACHER
        other_teacher_user.save()

        TeacherProfile.objects.create(
            user=other_teacher_user,
            subjects="Historia del arte",
            hourly_rate=Decimal("35.00"),
            bio="Especialista en arte renacentista",
            availability=[TeacherProfile.Availability.AFTERNOON],
        )

    def test_requires_student_role(self):
        self.client.login(username="profe1", password="pass1234")

        response = self.client.get(reverse("accounts:teacher_search"))

        self.assertRedirects(response, reverse("accounts:home"))

    def test_student_can_filter_by_subject_and_availability(self):
        self.client.login(username="alumna", password="pass1234")

        response = self.client.get(
            reverse("accounts:teacher_search"),
            {"subject": "fisica", "availability": [TeacherProfile.Availability.MORNING]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fisica avanzada")
        self.assertNotContains(response, "Historia del arte")

    def test_student_can_view_and_select_teacher(self):
        self.client.login(username="alumna", password="pass1234")

        detail_url = reverse("accounts:teacher_detail", args=[self.teacher_profile.pk])

        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Fisica avanzada")

        post_response = self.client.post(detail_url, follow=True)
        self.assertRedirects(post_response, detail_url)
        self.assertContains(post_response, "Has seleccionado a Luis Gomez")
