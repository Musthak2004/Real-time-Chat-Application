from django.conf import settings
from django.db import models


class Conversation(models.Model):

    CONVERSATION_TYPES = (
        ("PRIVATE", "Private"),
        ("GROUP", "Group"),
    )

    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default="PRIVATE",
        verbose_name="type",
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="group name",
    )

    image = models.ImageField(
        upload_to="conversation_images/",
        blank=True,
        null=True,
        verbose_name="group image",
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
        verbose_name="participants",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_conversations",
        verbose_name="created by",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created at",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="updated at",
    )

    class Meta:
        verbose_name = "conversation"
        verbose_name_plural = "conversations"

    def __str__(self):
        if self.conversation_type == "GROUP":
            return self.name or f"Group ({self.id})"
        participants = self.participants.values_list("username", flat=True)
        return ", ".join(participants) or f"Conversation {self.id}"


class ConversationMember(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="conversation",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_memberships",
        verbose_name="user",
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="joined at",
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name="admin",
    )

    is_muted = models.BooleanField(
        default=False,
        verbose_name="muted",
    )

    class Meta:
        verbose_name = "conversation member"
        verbose_name_plural = "conversation members"
        unique_together = (
            "conversation",
            "user",
        )

    def __str__(self):
        return f"{self.user.username} in {self.conversation}"