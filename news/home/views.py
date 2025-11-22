from django.shortcuts import render
from .models import Contact

def index(request):
    return render(request, "home/index.html")

def about(request):
    return render(request, "home/about.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")

        # Data database me save karo
        Contact.objects.create(name=name, message=message)

        return render(request, "home/contact.html", {
            "success": True,
            "name": name
        })

    return render(request, "home/contact.html")
