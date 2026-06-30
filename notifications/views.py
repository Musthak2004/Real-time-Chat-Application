from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views.generic import (
    ListView,
    View,
)

from .models import Notification

class NotificationListView(
    LoginRequiredMixin,
    ListView
):

    model = Notification

    template_name = (
        "notifications/notification_list.html"
    )

    context_object_name = (
        "notifications"
    )

    paginate_by = 50

    def get_queryset(self):

        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related("sender")


class MarkAsReadView(
    LoginRequiredMixin,
    View
):

    def post(
        self,
        request,
        pk
    ):

        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )

        notification.is_read = True

        notification.save()

        messages.success(
            request,
            "Notification marked as read.",
        )

        return redirect(
            "notifications:list"
        )


class MarkAllAsReadView(
    LoginRequiredMixin,
    View
):

    def post(
        self,
        request
    ):

        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

        if count:
            messages.success(
                request,
                f"{count} notification{'s' if count != 1 else ''} marked as read.",
            )

        return redirect(
            "notifications:list"
        )