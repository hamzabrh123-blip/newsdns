from django.db import models


class FSJJewellery(models.Model):
    CATEGORY_CHOICES = [
        ("Ring", "Ring"),
        ("Necklace", "Necklace"),
        ("Earrings", "Earrings"),
        ("Bangle", "Bangle"),
        ("Chain", "Chain"),
        ("Pendant", "Pendant"),
        ("Bracelet", "Bracelet"),
        ("Other", "Other"),
    ]

    PURITY_CHOICES = [
        ("24K", "24K Gold"),
        ("22K", "22K Gold"),
        ("18K", "18K Gold"),
        ("14K", "14K Gold"),
        ("Silver", "Silver"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Ring",
    )
    purity = models.CharField(
        max_length=20,
        choices=PURITY_CHOICES,
        default="22K",
    )
    weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="fsj_jewellery/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fsj_jewellery_items"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name