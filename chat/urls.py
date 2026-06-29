from django.urls import path

from .views import (
    ConversationListView,
    ConversationDetailView,
    ConversationCreateView,
)

app_name = "chat"

urlpatterns = [

    path(
        "",
        ConversationListView.as_view(),
        name="conversation_list"
    ),

    path(
        "create/",
        ConversationCreateView.as_view(),
        name="conversation_create"
    ),

    path(
        "<int:pk>/",
        ConversationDetailView.as_view(),
        name="conversation_detail"
    ),
]