from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomePageTest(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse("pages:home"))
        self.assertTemplateUsed(response, "home.html")

    def test_anonymous_user(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, "Welcome to ChatApp")

    def test_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
