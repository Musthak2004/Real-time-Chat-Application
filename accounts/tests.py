from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignUpTest(TestCase):

    def test_signup_page_status_code(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_signup_redirects_to_home(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertRedirects(response, reverse("pages:home"))


class ProfileTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
