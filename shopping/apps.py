import os
import sys
from django.apps import AppConfig

class ShoppingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping'

    def ready(self):
        # Migrations ya management commands chalate waqt scheduler start na ho
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv or 'check_stock' in sys.argv:
            return

        # Local server (runserver) mein double execution rokne ke liye, aur Render (gunicorn) mein allow karne ke liye
        is_runserver = 'runserver' in sys.argv
        if is_runserver and os.environ.get('RUN_MAIN') != 'true':
            return

        from datetime import datetime, timedelta
        from apscheduler.schedulers.background import BackgroundScheduler
        from django.core.management import call_command

        def run_stock_checker():
            try:
                call_command('check_stock')
            except Exception as e:
                print(f"Background Stock Check Error: {e}")

        scheduler = BackgroundScheduler()
        # Server start hone ke 1 minute baad pehli baar chalega, aur fir har 4 ghante mein auto-run hoga
        first_run = datetime.now() + timedelta(minutes=1)
        scheduler.add_job(run_stock_checker, 'interval', hours=4, next_run_time=first_run)
        scheduler.start()