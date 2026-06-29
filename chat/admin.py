from django.contrib import admin

from .models import (
    Conversation,
    ConversationMember,
)


class ConversationMemberInline(
    admin.TabularInline
):

    model = ConversationMember

    extra = 0

    readonly_fields = (
        "joined_at",
    )


@admin.register(Conversation)
class ConversationAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "conversation_type",
        "name",
        "created_by",
        "created_at",
    )

    list_filter = (
        "conversation_type",
    )

    search_fields = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    filter_horizontal = (
        "participants",
    )

    inlines = [
        ConversationMemberInline
    ]


@admin.register(ConversationMember)
class ConversationMemberAdmin(
    admin.ModelAdmin
):

    list_display = (
        "conversation",
        "user",
        "is_admin",
        "is_muted",
        "joined_at",
    )

    list_filter = (
        "is_admin",
        "is_muted",
    )

    search_fields = (
        "user__username",
        "conversation__name",
    )

    readonly_fields = (
        "joined_at",
    )