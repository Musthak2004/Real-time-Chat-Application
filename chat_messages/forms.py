from django import forms

from .models import Message


class MessageForm(forms.ModelForm):

    class Meta:

        model = Message

        fields = (
            "content",
            "attachment",
            "message_type",
        )

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Type a message...",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        msg_type = cleaned_data.get("message_type")
        content = cleaned_data.get("content")
        attachment = cleaned_data.get("attachment")

        if msg_type == "TEXT" and not content:
            self.add_error(
                "content",
                "Message content is required for text messages.",
            )

        if msg_type in ("IMAGE", "VIDEO", "FILE", "AUDIO") and not attachment:
            self.add_error(
                "attachment",
                f"An attachment is required for {msg_type.lower()} messages.",
            )

        return cleaned_data