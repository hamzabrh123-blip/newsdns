from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='optimize_image')
def optimize_image(image_url):
    """
    ImgBB या किसी भी बाहरी URL को Cloudinary के जरिए ऑप्टिमाइज़ करके भेजता है।
    """
    if not image_url:
        return "/static/logo.png"

    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'dvoqsrkkq')
    base_url = getattr(settings, 'CLOUDINARY_BASE_URL', f"https://res.cloudinary.com/{cloud_name}/image/fetch/")
    params = getattr(settings, 'CLOUDINARY_OPTIMIZE_PARAMS', 'f_auto,q_auto,w_800/')

    # अगर इमेज का URL http से शुरू होता है और पहले से क्लाउडिनरी का नहीं है
    if image_url.startswith("http") and "res.cloudinary.com" not in image_url:
        return f"{base_url}{params}{image_url}"
    
    return image_url
