from celery import shared_task

from chat.models import Conversation
from notifications.models import Notification


@shared_task
def create_notification(conversation_id, sender_id, content):

    conversation = Conversation.objects.get(pk=conversation_id)
    sender_name = conversation.participants.get(pk=sender_id).username

    for participant in conversation.participants.exclude(pk=sender_id):
        Notification.objects.create(
            recipient=participant,
            sender_id=sender_id,
            notification_type="MESSAGE",
            title=f"New message from {sender_name}",
            message=content[:100] or "[attachment]",
        )
