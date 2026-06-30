from celery import shared_task

from chat.models import Conversation
from notifications.models import Notification


@shared_task(bind=True, max_retries=2)
def create_notification(self, conversation_id, sender_id, sender_username, content):

    try:
        conversation = Conversation.objects.only("pk").get(pk=conversation_id)
    except Conversation.DoesNotExist:
        return

    participants = conversation.participants.exclude(pk=sender_id).only("pk")

    for participant in participants.iterator():
        Notification.objects.create(
            recipient=participant,
            sender_id=sender_id,
            notification_type="MESSAGE",
            title=f"New message from {sender_username}",
            message=content[:100] or "[attachment]",
        )
