import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# 1. Start application
application = get_wsgi_application()

# 2. Force Migration (Ye table banayega)
try:
    print("Bhai, Migration shuru ho rahi hai...")
    call_command('migrate', '--run-syncdb', '--noinput')
    print("Bhai, Table V6 ban gayi!")
except Exception as e:
    print(f"Migration mein error: {e}")

# 3. Create Superuser (Sirf table banne ke baad)
try:
    User = get_user_model()
    if not User.objects.filter(username="adminauto").exists():
        User.objects.create_superuser("adminauto", "admin@example.com", "Admin@12345")
        print("Superuser bhi ban gaya!")
except Exception as e:
    print(f"Superuser error (Shayad table abhi nahi bani): {e}")
