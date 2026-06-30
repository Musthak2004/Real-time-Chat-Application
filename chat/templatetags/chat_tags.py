from django import template

register = template.Library()


@register.filter
def display_name(conversation, user):
    if conversation.conversation_type == "GROUP":
        return conversation.name or "Unnamed Group"
    for participant in conversation.participants.all():
        if participant.pk != user.pk:
            return participant.username
    return "Unknown"


@register.filter
def display_initial(conversation, user):
    if conversation.conversation_type == "GROUP":
        return (conversation.name or "G")[0].upper()
    for participant in conversation.participants.all():
        if participant.pk != user.pk:
            return participant.username[0].upper()
    return "?"


@register.filter
def display_status(conversation, user):
    if conversation.conversation_type == "GROUP":
        return f"{len(conversation.participants.all())} members"
    for participant in conversation.participants.all():
        if participant.pk != user.pk:
            if participant.is_online:
                return "Online"
            return "Offline"
    return "Offline"
