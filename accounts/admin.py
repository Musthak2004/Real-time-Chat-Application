from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "id",
        "username",
        "email",
        "is_online",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_online",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = (
        "username",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "phone_number",
                    "profile_picture",
                    "bio",
                    "date_of_birth",
                    "is_online",
                    "last_seen",
                )
            },
        ),
    )

    readonly_fields = (
        "last_seen",
        "created_at",
        "updated_at",
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "email",
                    "phone_number",
                )
            },
        ),
    )