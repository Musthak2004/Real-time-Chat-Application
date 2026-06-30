from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from chat.models import Conversation
from notifications.tasks import create_notification

from .forms import MessageForm
from .models import Message


class MessageCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Message

    form_class = MessageForm

    template_name = "chat_messages/message_form.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["conversation"] = get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
            participants=self.request.user,
        )

        context["chat_messages"] = (
            context["conversation"]
            .messages
            .select_related("sender")
            .order_by("created_at")
        )

        return context

    def form_valid(self, form):

        conversation = get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
            participants=self.request.user,
        )

        form.instance.sender = self.request.user

        form.instance.conversation = conversation

        response = super().form_valid(form)

        create_notification.delay(
            conversation_id=conversation.pk,
            sender_id=self.request.user.pk,
            content=form.instance.content or "",
        )

        return response

    def get_success_url(self):

        return reverse(
            "chat:conversation_detail",
            kwargs={
                "pk": self.kwargs["conversation_id"]
            }
        )