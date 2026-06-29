from django.contrib import admin

from .models import (
    Message,
    MessageRead,
    MessageReaction,
)


class MessageReadInline(admin.TabularInline):

    model = MessageRead

    extra = 0

    readonly_fields = (
        "read_at",
    )


class MessageReactionInline(admin.TabularInline):

    model = MessageReaction

    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "sender",
        "message_type",
        "is_edited",
        "created_at",
    )

    list_filter = (
        "message_type",
        "is_edited",
    )

    search_fields = (
        "content",
        "sender__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "conversation",
        "sender",
    )

    inlines = [
        MessageReadInline,
        MessageReactionInline,
    ]


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):

    list_display = (
        "message",
        "user",
        "read_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "read_at",
    )


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):

    list_display = (
        "message",
        "user",
        "emoji",
    )

    search_fields = (
        "user__username",
    )