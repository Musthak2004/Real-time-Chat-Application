from django import template

register = template.Library()


@register.filter
def display_name(conversation, user):
    if conversation.conversation_type == "GROUP":
        return conversation.name or "Unnamed Group"
    other = conversation.participants.exclude(pk=user.pk).first()
    return other.username if other else "Unknown"


@register.filter
def display_initial(conversation, user):
    if conversation.conversation_type == "GROUP":
        return (conversation.name or "G")[0].upper()
    other = conversation.participants.exclude(pk=user.pk).first()
    return other.username[0].upper() if other else "?"


@register.filter
def display_status(conversation, user):
    if conversation.conversation_type == "GROUP":
        return f"{conversation.participants.count()} members"
    other = conversation.participants.exclude(pk=user.pk).first()
    if other and other.is_online:
        return "Online"
    return "Offline"
