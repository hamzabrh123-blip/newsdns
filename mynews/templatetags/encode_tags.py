from django import template
from mynews.utils import encode_id

register = template.Library()

@register.filter
def encode_news_id(value):
    return encode_id(value)

