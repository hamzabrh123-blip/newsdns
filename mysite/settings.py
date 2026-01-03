import os
from pathlib import Path
import dj_database_url

# ---------------- BASE ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")
DEBUG = True # Live hone par ise False kar dena

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "halchal.onrender.com",
    "halchal.up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://halchal.up.railway.app",
    "http://halchal.up.railway.app",
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
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"), # Sirf naam likhna hai
        conn_max_age=600,
        ssl_require=True
    )
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
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_NAME", "dvoqsrkkq"),
    "API_KEY": os.environ.get("CLOUDINARY_KEY", "468226887694915"),
    "API_SECRET": os.environ.get("CLOUDINARY_SECRET", "1j2X6nWy-0xZqdbr6e9puCVC8VE"),
}

# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "hamzabrh@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "brjboidzxxciayvw")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------- CKEDITOR ----------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_STORAGE_BACKEND = "cloudinary_storage.storage.MediaCloudinaryStorage"
