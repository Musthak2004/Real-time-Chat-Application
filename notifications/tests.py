from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification


class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_str(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="SYSTEM",
            title="Welcome!",
            message="Welcome to the app",
        )
        self.assertEqual(str(notif), "testuser - Welcome!")

    def test_str_truncates_long_title(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="SYSTEM",
            title="x" * 100,
            message="Test",
        )
        result = str(notif)
        self.assertTrue(len(result) < 70)

    def test_default_is_read(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="MESSAGE",
            title="Test",
            message="Test",
        )
        self.assertFalse(notif.is_read)

    def test_get_absolute_url(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="MESSAGE",
            title="Test",
            message="Test",
        )
        self.assertEqual(notif.get_absolute_url(), reverse("notifications:list"))

    def test_ordering(self):
        n1 = Notification.objects.create(
            recipient=self.user, sender=self.user,
            notification_type="MESSAGE", title="First", message="First",
        )
        n2 = Notification.objects.create(
            recipient=self.user, sender=self.user,
            notification_type="MESSAGE", title="Second", message="Second",
        )
        notifications = Notification.objects.all()
        self.assertEqual(list(notifications), [n2, n1])


class NotificationListViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("notifications:list"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('notifications:list')}",
        )

    def test_shows_empty_notifications(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All caught up!")

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertTemplateUsed(response, "notifications/notification_list.html")

    def test_shows_own_notifications_only(self):
        other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )
        own = Notification.objects.create(
            recipient=self.user, sender=self.user,
            notification_type="MESSAGE", title="Own", message="Own",
        )
        Notification.objects.create(
            recipient=other, sender=other,
            notification_type="MESSAGE", title="Other", message="Other",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertContains(response, "Own")
        self.assertNotContains(response, "Other")

    def test_includes_unread_count(self):
        Notification.objects.create(
            recipient=self.user, sender=self.user,
            notification_type="MESSAGE", title="Test", message="Test",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertIn("unread_count", response.context)
        self.assertEqual(response.context["unread_count"], 1)


class MarkAsReadViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

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
        self.assertRedirects(response, reverse("notifications:list"))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_requires_login(self):
        response = self.client.post(
            reverse("notifications:read", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_only_owner_can_mark_read(self):
        other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )
        notification = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notification_type="MESSAGE",
            title="Test",
            message="Test message",
        )
        self.client.force_login(other)
        response = self.client.post(
            reverse("notifications:read", kwargs={"pk": notification.pk})
        )
        self.assertEqual(response.status_code, 404)


class MarkAllAsReadViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

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
        self.assertRedirects(response, reverse("notifications:list"))
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=True).count(),
            3,
        )

    def test_requires_login(self):
        response = self.client.post(reverse("notifications:read_all"))
        self.assertEqual(response.status_code, 302)

    def test_does_not_mark_other_users(self):
        other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )
        Notification.objects.create(
            recipient=other, sender=other,
            notification_type="MESSAGE", title="Other", message="Other",
        )
        self.client.force_login(self.user)
        self.client.post(reverse("notifications:read_all"))
        other_notif = Notification.objects.get(recipient=other)
        self.assertFalse(other_notif.is_read)
