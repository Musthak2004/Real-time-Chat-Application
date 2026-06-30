from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Prefetch
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from chat_messages.models import Message

from .forms import ConversationForm
from .models import Conversation

class ConversationListView(
    LoginRequiredMixin,
    ListView
):

    model = Conversation

    template_name = "chat/conversation_list.html"

    context_object_name = "conversations"

    paginate_by = 50

    def get_queryset(self):

        return (
            self.request.user.conversations
            .prefetch_related("participants")
            .annotate(member_count=Count("participants"))
            .order_by("-updated_at")
        )

class ConversationDetailView(
    LoginRequiredMixin,
    DetailView
):

    model = Conversation

    template_name = "chat/conversation_detail.html"

    context_object_name = "conversation"

    def get_queryset(self):

        return self.request.user.conversations.prefetch_related("participants")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["chat_messages"] = (
            self.object.messages
            .select_related("sender")
            .order_by("created_at")
        )

        return context

class ConversationCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    model = Conversation

    form_class = ConversationForm

    template_name = "chat/conversation_form.html"

    success_url = reverse_lazy(
        "chat:conversation_list"
    )

    success_message = "Conversation created successfully."

    def form_valid(
        self,
        form
    ):

        form.instance.created_by = (
            self.request.user
        )

        response = super().form_valid(
            form
        )

        self.object.participants.add(
            self.request.user
        )

        return response