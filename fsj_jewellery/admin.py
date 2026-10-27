from django.contrib import admin
from .models import FSJJewellery


@admin.register(FSJJewellery)
class FSJJewelleryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "purity",
        "weight_grams",
        "price",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "purity", "is_active")
    search_fields = ("name", "description")
    list_editable = ("is_active", "price")
    ordering = ("-created_at",)