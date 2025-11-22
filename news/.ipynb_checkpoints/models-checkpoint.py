from django.db import models

class News(models.Model):
    headline = models.charField(max_lenght=200)
    youtube_url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False) #important news flag

    def __str__(self):
        return f"{self.headline} ({self.date.strftie('%d-%m-%Y')})"