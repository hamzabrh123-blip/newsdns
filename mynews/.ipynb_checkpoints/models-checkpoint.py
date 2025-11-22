from django.db import models

class News(models.Model):
    headline = models.CharField(max_length=200)
    youtube_url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False) #important news flag

    def __str__(self):
        return f"{self.headline} ({self.date.strftime('%d-%m-%Y')})"