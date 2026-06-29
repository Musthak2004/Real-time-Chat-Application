from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from .forms import ConversationForm
from .models import Conversation

class ConversationListView(
    LoginRequiredMixin,
    ListView
):

    model = Conversation

    template_name = "chat/conversation_list.html"

    context_object_name = "conversations"

    def get_queryset(self):

        return self.request.user.conversations.all().order_by("-updated_at")
    
class ConversationDetailView(
    LoginRequiredMixin,
    DetailView
):

    model = Conversation

    template_name = "chat/conversation_detail.html"

    context_object_name = "conversation"

    def get_queryset(self):

        return self.request.user.conversations.all()

class ConversationCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Conversation

    form_class = ConversationForm

    template_name = "chat/conversation_form.html"

    success_url = reverse_lazy(
        "chat:conversation_list"
    )

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