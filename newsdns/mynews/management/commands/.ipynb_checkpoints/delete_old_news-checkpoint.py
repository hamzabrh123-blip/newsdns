from django.core.management.base import BaseCommand

from mynews.models import News

from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Delete News older than 30 days unless it's important"

    def handle(self, *args, **kwrgs):
        cutoff = datetime.now() - timedelta(days=30)
        old_news = News.objects.filter(date__lt=cutoff, is_important=False)
        count = old_news.count()
        old_news.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} old non-important news.'))