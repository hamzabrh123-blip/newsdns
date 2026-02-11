from django import template
import re

register = template.Library()

@register.filter
def yt_embed(url):
    """
    Converts any YouTube URL (watch, shorts, youtu.be) to embed format
    """

    if not url:
        return ""

    # Extract 11 character video ID
    match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([a-zA-Z0-9_-]{11})", url)

    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?rel=0"

    return ""
