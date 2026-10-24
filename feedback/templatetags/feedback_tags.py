
from django import template

from feedback.models import Feedback
from shopping.models import Product, Category

register = template.Library()


@register.inclusion_tag("feedback/feedback_section.html")
def feedback_section(target):
    if isinstance(target, Product):
        target_type = "product"
        slug = target.slug
        feedback_list = Feedback.objects.filter(
            product=target,
            status="approved",
        ).select_related("product").order_by("-created_at")

    elif isinstance(target, Category):
        target_type = "category"
        slug = target.slug
        feedback_list = Feedback.objects.filter(
            category=target,
            status="approved",
        ).select_related("category").order_by("-created_at")

    else:
        target_type = ""
        slug = ""
        feedback_list = Feedback.objects.none()

    return {
        "target_type": target_type,
        "target_slug": slug,
        "feedback_list": feedback_list,
    }
