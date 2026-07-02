import uuid
import time

from django.db import models
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField
from unidecode import unidecode

from .utils import process_and_upload_to_imgbb, ping_google_indexing


# ==========================================
# 1. CATEGORY
# ==========================================

class Category(models.Model):

    name = models.CharField(max_length=100)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    description = RichTextUploadingField(
        blank=True,
        null=True
    )

    meta_keywords = models.TextField(
        blank=True,
        null=True
    )

    meta_description = models.TextField(
        blank=True,
        null=True
    )

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(
                unidecode(self.name)
            )

        image_url_val = str(self.image_url) if self.image_url else ""

        is_new_image = bool(
            self.image and "i.ibb.co" not in image_url_val
        )

        super().save(*args, **kwargs)

        if is_new_image:
            self.handle_upload()

    # ==========================================
    # IMAGE UPLOAD
    # ==========================================

    def handle_upload(self):

        try:

            new_url = process_and_upload_to_imgbb(
                self,
                is_shop=True
            )

            if new_url:

                Category.objects.filter(
                    pk=self.pk
                ).update(
                    image_url=new_url,
                    image=None
                )

        except Exception as e:

            print(f"Category Upload Error: {e}")

    def __str__(self):

        return self.name


# ==========================================
# 2. PRODUCT MANAGER
# ==========================================

class ProductManager(models.Manager):

    def search_and_filter(self, query=None, max_price=None):

        queryset = self.get_queryset().filter(
            is_available=True
        )

        if query:

            queryset = queryset.filter(
                title__icontains=query
            )

        if max_price and str(max_price).isdigit():

            queryset = queryset.filter(
                variants__coupons__selling_price__lte=int(max_price)
            )

        return queryset.distinct()


# ==========================================
# 3. PRODUCT
# ==========================================

class Product(models.Model):

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    mrp_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    price_display = models.CharField(
        max_length=100
    )

    long_description = RichTextUploadingField()

    meta_description = models.TextField(
        blank=True,
        null=True
    )

    meta_keywords = models.TextField(
        blank=True,
        null=True
    )

    is_available = models.BooleanField(
        default=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = ProductManager()

    # ==========================================
    # PRODUCT URL
    # ==========================================

    def get_absolute_url(self):

        return f"/product/{self.slug}/"

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = (
                f"{slugify(unidecode(self.title))[:80]}"
                f"-{str(uuid.uuid4())[:6]}"
            )

        super().save(*args, **kwargs)

        try:

            ping_google_indexing(
                f"https://uttarworld.com{self.get_absolute_url()}"
            )

        except Exception as e:

            print(f"Google Indexing Error: {e}")

    def __str__(self):

        return self.title


# ==========================================
# 4. PRODUCT VARIANT
# ==========================================

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        related_name='variants',
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to='variants/',
        null=True,
        blank=True
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    earn_karo_url = models.URLField(
        max_length=700
    )

    variant_code = models.CharField(
        max_length=20,
        blank=True,
        unique=True
    )

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.variant_code:

            prefix = "".join(
                [word[0] for word in self.product.title.split()[:2]]
            ).upper()

            self.variant_code = (
                f"{prefix}-{str(uuid.uuid4())[:4].upper()}"
            )

        super().save(*args, **kwargs)

        image_url_val = str(self.image_url) if self.image_url else ""

        is_new_image = bool(
            self.image and "i.ibb.co" not in image_url_val
        )

        if is_new_image:
            self.handle_variant_upload()

    # ==========================================
    # IMAGE UPLOAD
    # ==========================================

    def handle_variant_upload(self):

        try:

            time.sleep(0.5)

            new_url = process_and_upload_to_imgbb(
                self,
                is_shop=True
            )

            if new_url:

                ProductVariant.objects.filter(
                    pk=self.pk
                ).update(
                    image_url=new_url,
                    image=None
                )

        except Exception as e:

            print(f"Variant Upload Error: {e}")

    def __str__(self):

        return f"{self.product.title} - {self.variant_code}"


# ==========================================
# 5. VARIANT STORE COUPON
# ==========================================

class VariantStoreCoupon(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='coupons'
    )

    store_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True
    )

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        if self.store_name and not self.coupon_code:

            try:

                from .models import StoreConfiguration

                config = StoreConfiguration.objects.filter(
                    store_name__iexact=self.store_name
                ).first()

                if config:
                    self.coupon_code = config.default_coupon_code

            except:
                pass

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.store_name} - {self.coupon_code}"


# ==========================================
# 6. HOME SLIDER
# ==========================================

class HomeSlider(models.Model):

    title = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to='sliders/',
        null=True,
        blank=True
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    link = models.URLField(
        max_length=500,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        image_url_val = str(self.image_url) if self.image_url else ""

        is_new_image = bool(
            self.image and "i.ibb.co" not in image_url_val
        )

        super().save(*args, **kwargs)

        if is_new_image:
            self.handle_upload()

    # ==========================================
    # IMAGE UPLOAD
    # ==========================================

    def handle_upload(self):

        try:

            new_url = process_and_upload_to_imgbb(
                self,
                is_shop=True
            )

            if new_url:

                HomeSlider.objects.filter(
                    pk=self.pk
                ).update(
                    image_url=new_url,
                    image=None
                )

        except Exception as e:

            print(f"Slider Upload Error: {e}")

    def __str__(self):

        return self.title if self.title else f"Slider {self.id}"


# ==========================================
# 7. DROPDOWN MENU
# ==========================================

class DropdownMenu(models.Model):

    menu_name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    categories = models.ManyToManyField(
        Category,
        related_name='dropdown_menus'
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.IntegerField(
        default=0
    )

    # ==========================================
    # SAVE
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(
                unidecode(self.menu_name)
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.menu_name


class HomeSection(models.Model):

    image = models.ImageField(
        upload_to='home_sections/',
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='home_sections',
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):

        if self.category:
            return self.category.name

        return "Home Section"
