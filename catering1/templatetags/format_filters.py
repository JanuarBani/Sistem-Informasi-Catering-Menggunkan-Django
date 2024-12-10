# myapp/templatetags/format_filters.py
from django import template

register = template.Library()


@register.filter
def format_number(value):
    try:
        # Format angka dengan pemisah ribuan
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value
