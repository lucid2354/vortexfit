from django import template

from shop.utils import money as _money

register = template.Library()


@register.filter
def money(value):
    try:
        return _money(value)
    except (TypeError, ValueError):
        return value
