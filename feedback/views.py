
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

from shopping.models import Product, Category
from .models import Feedback


@require_POST
def submit_feedback(request, target_type, slug):
    if target_type == "product":
        target = get_object_or_404(Product, slug=slug, is_available=True)
        feedback_data = {"product": target, "category": None}
    elif target_type == "category":
        target = get_object_or_404(Category, slug=slug)
        feedback_data = {"product": None, "category": target}
    else:
        messages.error(request, "Invalid feedback destination.")
        return redirect("/")

    author_name = request.POST.get("author_name", "").strip()
    comment = request.POST.get("comment", "").strip()
    rating_value = request.POST.get("rating", "").strip()

    if not author_name or not comment:
        messages.error(request, "Naam aur comment dono bharna zaroori hai.")
    elif len(author_name) > 100:
        messages.error(request, "Naam 100 characters se chhota rakhein.")
    elif len(comment) > 5000:
        messages.error(request, "Comment 5000 characters se chhota rakhein.")
    else:
        rating = None

        if rating_value:
            if rating_value not in {"1", "2", "3", "4", "5"}:
                messages.error(request, "Rating 1 se 5 stars ke beech honi chahiye.")
                return redirect_back(request, target_type, slug)

            rating = int(rating_value)

        Feedback.objects.create(
            **feedback_data,
            author_name=author_name,
            comment=comment,
            rating=rating,
            status="pending",
        )

        messages.success(
            request,
            "Shukriya! Aapka feedback review ke liye submit ho gaya hai.",
        )

    return redirect_back(request, target_type, slug)


def redirect_back(request, target_type, slug):
    fallback = (
        f"/shopping/product/{slug}/"
        if target_type == "product"
        else f"/shopping/category/{slug}/"
    )

    referer = request.META.get("HTTP_REFERER", "")
    if url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)

    return redirect(fallback)
