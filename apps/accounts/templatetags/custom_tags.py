from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    if not value:
        return []
    return value.split(arg)
