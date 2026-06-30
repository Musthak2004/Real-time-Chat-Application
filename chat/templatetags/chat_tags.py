from django import template

register = template.Library()


@register.filter
def display_name(conversation, user):
    return conversation.display_name(user)


@register.filter
def display_initial(conversation, user):
    return conversation.display_initial(user)


@register.filter
def display_status(conversation, user):
    return conversation.display_status(user)
