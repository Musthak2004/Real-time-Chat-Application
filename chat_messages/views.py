from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from chat.models import Conversation

from .forms import MessageForm
from .models import Message


class MessageCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Message

    form_class = MessageForm

    template_name = "chat_messages/message_form.html"

    def form_valid(self, form):

        conversation = get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
            participants=self.request.user,
        )

        form.instance.sender = self.request.user

        form.instance.conversation = conversation

        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy(
            "chat:conversation_detail",
            kwargs={
                "pk": self.kwargs["conversation_id"]
            }
        )