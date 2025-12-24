import random
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.core.cache import cache
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import News, Comment, AdminOTP

ADMIN_EMAIL = "hamzabrh@gmail.com"


# ================= ADMIN LOGIN =================
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email != ADMIN_EMAIL:
            messages.error(request, "You are not authorized!")
            return redirect("admin_login")

        otp = str(random.randint(100000, 999999))
        AdminOTP.objects.create(email=email, otp=otp)

        send_mail(
            "Admin Login OTP",
            f"Your OTP is: {otp}",
            ADMIN_EMAIL,
            [email],
            fail_silently=False,
        )

        request.session["admin_email"] = email
        return redirect("admin_verify")

    return render(request, "admin_login.html")


def admin_verify(request):
    if request.method == "POST":
        entered = request.POST.get("otp")
        email = request.session.get("admin_email")

        data = AdminOTP.objects.filter(email=email).last()

        if data and data
