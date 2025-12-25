import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
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

        # Purana OTP delete kar do
        AdminOTP.objects.filter(email=email).delete()

        AdminOTP.objects.create(email=email, otp=otp)

        send_mail(
            "Admin Login OTP",
            f"Your OTP is: {otp}",
            ADMIN_EMAIL,
            [email],
            fail_silently=False,
        )

        request.session["admin_email"] = email
        messages.success(request, "OTP sent to your email")
        return redirect("admin_verify")

    return render(request, "admin_login.html")


# ================= ADMIN OTP VERIFY =================
def admin_verify(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        email = request.session.get("admin_email")

        if not email:
            messages.error(request, "Session expired. Please login again.")
            return redirect("admin_login")

        data = AdminOTP.objects.filter(email=email).last()

        if data and data.otp == entered_otp:
            data.delete()  # OTP reuse na ho

            request.session["is_admin"] = True
            messages.success(request, "Admin login successful")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("admin_verify")

    return render(request, "admin_verify.html")


# ================= ADMIN DASHBOARD =================
def admin_dashboard(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    news_count = News.objects.count()
    comment_count = Comment.objects.count()

    context = {
        "news_count": news_count,
        "comment_count": comment_count,
    }

    return render(request, "admin_dashboard.html", context)


# ================= ADMIN LOGOUT =================
def admin_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect("admin_login")
