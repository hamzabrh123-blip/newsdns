from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .utils import get_common_sidebar_data

def contact_us(request):
    success = False
    if request.method == "POST":
        try:
            send_mail("Contact", request.POST.get('message'), settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            success = True
        except: pass
    context = {"success": success}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")