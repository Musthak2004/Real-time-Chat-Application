from django.conf import settings
from django.db import models

from chat.models import Conversation


class Message(models.Model):

    MESSAGE_TYPES = (
        ("TEXT", "Text"),
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
        ("FILE", "File"),
        ("AUDIO", "Audio"),
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="conversation",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="sender",
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default="TEXT",
        verbose_name="type",
    )

    content = models.TextField(
        blank=True,
        verbose_name="content",
    )

    attachment = models.FileField(
        upload_to="chat_attachments/",
        blank=True,
        null=True,
        verbose_name="attachment",
    )

    is_edited = models.BooleanField(
        default=False,
        verbose_name="edited",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="sent at",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="updated at",
    )

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50] or '[attachment]'}"


class MessageRead(models.Model):

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="read_receipts",
        verbose_name="message",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="read_receipts",
        verbose_name="user",
    )

    read_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="read at",
    )

    class Meta:
        verbose_name = "read receipt"
        verbose_name_plural = "read receipts"
        unique_together = (
            "message",
            "user",
        )

    def __str__(self):
        return f"{self.user.username} read #{self.message.id}"


class MessageReaction(models.Model):

    REACTIONS = (
        ("👍", "Like"),
        ("❤️", "Love"),
        ("😂", "Laugh"),
        ("😮", "Wow"),
        ("😢", "Sad"),
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name="message",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name="user",
    )

    emoji = models.CharField(
        max_length=5,
        choices=REACTIONS,
        verbose_name="emoji",
    )

    class Meta:
        verbose_name = "reaction"
        verbose_name_plural = "reactions"
        unique_together = (
            "message",
            "user",
        )

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji}"