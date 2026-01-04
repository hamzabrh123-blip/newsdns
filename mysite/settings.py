import os
from pathlib import Path
import dj_database_url

# ---------------- BASE ----------------
BASE_DIR = Path(__file__).resolve().parent.parent





# ---------------- SECURITY ----------------
# Render Environment se uthayega, nahi milega toh default use karega (Crash nahi hoga)
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-up-halchal-123-aDc-439-082")

DEBUG = True # Sab theek hone ke baad False kar dena

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "halchal.onrender.com", 
]

CSRF_TRUSTED_ORIGINS = [
    "https://halchal.onrender.com",
    "http://halchal.onrender.com",
]
# ---------------- APPS ----------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "mynews",
    "ckeditor",
    "ckeditor_uploader",
    "cloudinary",
]

# ---------------- MIDDLEWARE ----------------
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

# ---------------- TEMPLATES ----------------
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
                # Temporary hata diya hai crash rokne ke liye
                # "mynews.context_processors.important_news",
                # "mynews.context_processors.site_visits",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ---------------- DATABASE ----------------
# Render par Database connect karne ka sabse safe tareeka:

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}

# SSL error ko handle karne ka sahi tareeka
if not DEBUG or os.environ.get('DATABASE_URL'):
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }
# ---------------- GENERAL ----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata" # India time set kiya hai
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- STATIC & MEDIA ----------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Isse error nahi aayega agar static folder na bhi ho
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    STATICFILES_DIRS = [STATIC_DIR]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------- CKEDITOR ----------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_STORAGE_BACKEND = "cloudinary_storage.storage.MediaCloudinaryStorage"
