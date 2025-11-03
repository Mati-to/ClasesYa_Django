from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
