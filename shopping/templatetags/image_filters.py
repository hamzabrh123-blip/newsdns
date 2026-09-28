from django import template
from urllib.parse import urlparse, urlunparse

register = template.Library()

@register.filter(name='clean_image_url')
def clean_image_url(raw_url):
    if not raw_url:
        return raw_url
    
    # 1. Question mark (?) ya uske baad ke kisi bhi parameter ko hatane ke liye split kar do
    base_url = raw_url.split('?')[0]
    
    # 2. Agar URL ke path mein image extension (.jpg, .jpeg, .png, .avif, .webp) hai, 
    # toh uske baad ka faltu text hatane ke liye thoda aur refine kar sakte hain.
    parsed = urlparse(base_url)
    
    # Clean tuple assemble karo bina query parameters ke
    clean_tuple = (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '', # params
        '', # query parameters bilkul uda diye!
        ''  # fragment
    )
    
    return urlunparse(clean_tuple)