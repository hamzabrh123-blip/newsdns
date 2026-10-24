
from django.contrib import admin
from django.utils import timezone

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "author_name",
        "feedback_target",
        "rating",
        "status",
        "created_at",
        "has_reply",
    )

    list_filter = (
        "status",
        "rating",
        "created_at",
    )

    search_fields = (
        "author_name",
        "comment",
        "admin_reply",
        "product__title",
        "category__name",
    )

  
    readonly_fields = (
        "product",
        "category",
        "created_at",
        "updated_at",
        "replied_at",
    )

    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ( "Visitor Feedback", {"fields": ( "product", "category", "author_name", "comment", "rating",)}, ),
        (
            "Moderation",
            {
                "fields": ("status",),
            },
        ),
        (
            "Your Reply",
            {
                "fields": ("admin_reply", "replied_at"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    actions = (
        "approve_feedback",
        "reject_feedback",
    )

    @admin.display(description="Product / Category")
    def feedback_target(self, obj):
        return obj.product or obj.category or "No target"

    @admin.display(boolean=True, description="Reply Added")
    def has_reply(self, obj):
        return bool(obj.admin_reply.strip())

    @admin.action(description="Approve selected feedback")
    def approve_feedback(self, request, queryset):
        updated = queryset.update(status="approved")
        self.message_user(
            request,
            f"{updated} feedback item(s) approved.",
        )

    @admin.action(description="Reject selected feedback")
    def reject_feedback(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(
            request,
            f"{updated} feedback item(s) rejected.",
        )

    def save_model(self, request, obj, form, change):
        if obj.admin_reply.strip():
            if not obj.replied_at:
                obj.replied_at = timezone.now()
        else:
            obj.replied_at = None

        super().save_model(request, obj, form, change)
