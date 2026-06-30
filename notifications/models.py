from django.conf import settings
from django.db import models


class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("MESSAGE", "New Message"),
        ("GROUP", "Group Invite"),
        ("REACTION", "Reaction"),
        ("CALL", "Call"),
        ("SYSTEM", "System"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        verbose_name="recipient",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        related_query_name="sent_notification",
        verbose_name="sender",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name="type",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="title",
    )

    message = models.TextField(
        verbose_name="message",
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name="read",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created at",
    )

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("notifications:list")

    def __str__(self):
        return f"{self.recipient.username} - {self.title[:50]}"