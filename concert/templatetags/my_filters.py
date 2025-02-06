from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def is_active(things, state):
    return things.filter(is_active=state)
