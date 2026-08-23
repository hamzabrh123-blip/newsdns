import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='replace_h1_with_h3')
def replace_h1_with_h3(value):
    if not value:
        return ""
    # Regex se saare <h1> aur </h1> ko <h3> aur </h3> mein badal do
    value = re.sub(r'<h1\b([^>]*)>', r'<h3\b\1>', value, flags=re.IGNORECASE)
    value = re.sub(r'</h1>', r'</h3>', value, flags=re.IGNORECASE)
    return mark_safe(value)