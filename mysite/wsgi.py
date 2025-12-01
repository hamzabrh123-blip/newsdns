"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = get_wsgi_application()

# AUTO CREATE SUPERUSER ON RENDER
import os
from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = get_wsgi_application()

try:
    User = get_user_model()
    username = "adminauto"
    email = "admin@example.com"
    password = "Admin@12345"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("Superuser created automatically!")
except Exception as e:
    print("Superuser creation failed:", str(e))
