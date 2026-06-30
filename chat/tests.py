from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Conversation


class ConversationListViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertEqual(response.status_code, 302)

    def test_shows_empty_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No conversations yet.")


class ConversationCreateViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("chat:conversation_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_private_conversation(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat:conversation_create"), {
            "conversation_type": "PRIVATE",
            "participants": [self.other.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertIn(self.user, Conversation.objects.first().participants.all())
