from django import forms

from .models import Conversation


class ConversationForm(forms.ModelForm):

    class Meta:

        model = Conversation

        fields = (
            "conversation_type",
            "name",
            "image",
            "participants",
        )

        widgets = {
            "conversation_type": forms.RadioSelect,
            "participants": forms.SelectMultiple(
                attrs={"size": 10}
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        conv_type = cleaned_data.get("conversation_type")
        name = cleaned_data.get("name")
        participants = cleaned_data.get("participants")

        if conv_type == "GROUP" and not name:
            self.add_error(
                "name",
                "Group name is required for group conversations.",
            )

        if not participants:
            self.add_error(
                "participants",
                "At least one participant is required.",
            )

        return cleaned_data