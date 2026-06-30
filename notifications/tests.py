from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification


class NotificationListViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 302)

    def test_shows_empty_notifications(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All caught up!")

    def test_mark_as_read(self):
        self.client.force_login(self.user)
        notification = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="MESSAGE",
            title="Test",
            message="Test message",
        )
        response = self.client.post(
            reverse("notifications:read", kwargs={"pk": notification.pk})
        )
        self.assertEqual(response.status_code, 302)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_as_read(self):
        self.client.force_login(self.user)
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                sender=self.user,
                notification_type="MESSAGE",
                title=f"Test {i}",
                message=f"Message {i}",
            )
        response = self.client.post(reverse("notifications:read_all"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=True).count(),
            3,
        )
