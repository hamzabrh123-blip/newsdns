import os
from pathlib import Path
import dj_database_url

# 1. Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY (All Sensitive Info Removed)
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-key-2026")

ALLOWED_HOSTS = [
    "uttarworld.com", 
    "www.uttarworld.com", 
    "newsdns.onrender.com", 
    ".onrender.com", 
    "localhost", 
    "127.0.0.1",
    "*" 
]

# 3. SSL & CSRF Fix (Only for Production/Render)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://uttarworld.com",
    "https://www.uttarworld.com",
    "https://newsdns.onrender.com"
]

# 4. INSTALLED APPS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "shopping",
    "mynews",
    "ckeditor",
    "ckeditor_uploader",
]

# 5. MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

# 6. TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mynews.context_processors.site_visits",
                "mynews.context_processors.news_data_processor", 
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# 7. DATABASE (Zero-Trace - Environment Based)
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}
DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# 8. STATIC FILES (Optimized)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "shopping" / "static",
    BASE_DIR / "mynews" / "static",
]

# 9. MEDIA (TERMINATED - No Local Storage)
# Humne inko zero kar diya hai taaki machine pe kuch save na ho
MEDIA_URL = "" 
MEDIA_ROOT = "" 

# 10. STORAGES
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False

# 11. CKEDITOR CONFIG (Safe Mode)
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

# 12. API KEYS & EMAIL (Everything from Environment)
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 13. I18N SETTINGS
LANGUAGE_CODE = 'hi'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True
