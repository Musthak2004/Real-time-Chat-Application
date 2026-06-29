from django.urls import path

from .views import MessageCreateView

app_name = "chat_messages"

urlpatterns = [

    path(
        "send/<int:conversation_id>/",
        MessageCreateView.as_view(),
        name="send_message"
    ),
]