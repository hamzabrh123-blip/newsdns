from django import template
import base64

register = template.Library()

@register.filter
def encode_news_id(value):
    try:
        return base64.urlsafe_b64encode(str(value).encode()).decode()
    except Exception:
        return value
