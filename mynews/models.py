import uuid
import os
from django.db import models, transaction
from django.utils.text import slugify
from unidecode import unidecode
from .utils import process_and_upload_to_imgbb, post_to_facebook
# ... बाकी imports वही रहेंगे

class News(models.Model):
    # ... बाकी fields वही रहेंगे
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True, help_text="बस फोटो चुनें, अपलोड अपने आप होगा")
    image_url = models.URLField(max_length=500, blank=True, null=True, editable=False) # इसे editable=False किया ताकि भ्रम न हो

    def save(self, *args, **kwargs):
        # 1. पहले Slug और बाकी Logic चलाएं
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:80]}-{str(uuid.uuid4())[:6]}"

        # 2. AUTO UPLOAD LOGIC
        # अगर नई इमेज डाली गई है
        if self.image:
            try:
                # ImgBB पर अपलोड करें
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    self.image_url = new_url
                    # अपलोड होने के बाद लोकल फाइल की ज़रूरत नहीं, इसे हटा सकते हैं
                    # self.image = None # अगर आप सर्वर पर फाइल नहीं रखना चाहते
            except Exception as e:
                print(f"Auto Upload Failed: {e}")

        super(News, self).save(*args, **kwargs)

        # 3. FB POSTING (वही पुराना लॉजिक)
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            transaction.on_commit(lambda: self.post_to_fb_handler())

    def post_to_fb_handler(self):
        if post_to_facebook(self):
            News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title
