from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='optimize_image')
def optimize_image(image_url):
    """
    यह फ़िल्टर ImgBB के लिंक को Cloudinary के रास्ते भेजता है 
    ताकि इमेज का साइज़ छोटा हो जाए और साइट फ़ास्ट खुले।
    """
    # 1. अगर इमेज यूआरएल खाली है
    if not image_url:
        return "/static/logo.png"

    # 2. Settings से डेटा उठाना (अगर वहां नहीं मिला तो ये डिफॉल्ट यूज़ करेगा)
    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'dvoqsrkkq')
    base_url = f"https://res.cloudinary.com/{cloud_name}/image/fetch/"
    params = getattr(settings, 'CLOUDINARY_OPTIMIZE_PARAMS', 'f_auto,q_auto,w_800/')

    # 3. सिर्फ बाहरी इमेज (ImgBB/HTTP) को ही बदलना है
    # अगर इमेज पहले से Cloudinary की है, तो उसे दोबारा न बदलें
    if str(image_url).startswith("http") and "res.cloudinary.com" not in str(image_url):
        return f"{base_url}{params}{image_url}"
    
    return image_url
