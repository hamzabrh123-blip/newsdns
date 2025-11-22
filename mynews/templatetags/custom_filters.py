from django import template

register = template.Library()

@register.filter
def yt_embed(url):
    """
    Converts YouTube watch URL to embed URL
    Example: https://www.youtube.com/watch?v=abc123 -> https://www.youtube.com/embed/abc123
    """
    if 'watch?v=' in url:
        return url.replace('watch?v=', 'embed/')
    return url
