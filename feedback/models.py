
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from shopping.models import Product, Category


class Feedback(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="feedback_entries",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="feedback_entries",
        null=True,
        blank=True,
    )

    author_name = models.CharField(max_length=100)
    comment = models.TextField()

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text="Optional rating from 1 to 5 stars.",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    admin_reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(product__isnull=False, category__isnull=True)
                    | Q(product__isnull=True, category__isnull=False)
                ),
                name="feedback_exactly_one_target",
            ),
        ]

    def __str__(self):
        target = self.product or self.category or "No target"
        return f"{self.author_name} - {target}"
