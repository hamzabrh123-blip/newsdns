from django.db import models
from .utils import process_and_upload_to_imgbb  # agar needed ho

def clean_image_url(url):
    if not url:
        return url
    return url.split('?')[0]


# ==========================================
# 1. PINTEREST BOARD MODEL
# ==========================================

class PinterestBoard(models.Model):
    name = models.CharField(max_length=255, verbose_name="Board Name")
    board_id = models.CharField(max_length=255, unique=True, verbose_name="Pinterest Board ID")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pinterest Board"
        verbose_name_plural = "Pinterest Boards"

    def __str__(self):
        return f"{self.name} ({self.board_id})"


# ==========================================
# 2. PINTEREST POST / PIN LOG MODEL
# ==========================================

class PinterestPost(models.Model):
    title = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500)
    link = models.URLField(max_length=500)
    board = models.ForeignKey(
        PinterestBoard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="pins"
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pinterest Post"
        verbose_name_plural = "Pinterest Posts"

    def save(self, *args, **kwargs):
        if self.image_url:
            self.image_url = clean_image_url(self.image_url)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title