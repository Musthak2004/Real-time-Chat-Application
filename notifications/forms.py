from django import forms

from .models import Notification


class NotificationForm(forms.ModelForm):

    class Meta:

        model = Notification

        fields = (
            "recipient",
            "sender",
            "notification_type",
            "title",
            "message",
        )
