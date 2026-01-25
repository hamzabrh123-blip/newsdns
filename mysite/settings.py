import os
from pathlib import Path
import dj_database_url

# ---------------- BASE ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-up-halchal-123-aDc-439-082")

DEBUG = False

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
    "cloudinary_storage", # Ye hamesha staticfiles se upar hona chahiye
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "cloudinary",
    "mynews",
    "ckeditor",
    "ckeditor_uploader",
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
                # "mynews.context_processors.important_news", # Error rokne ke liye band kiya hai
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ---------------- DATABASE ----------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=0,
    )
}

DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}

# ---------------- GENERAL ----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata" 
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- STATIC & MEDIA ----------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    STATICFILES_DIRS = [STATIC_DIR]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------- CLOUDINARY SETTINGS ----------------
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------- CKEDITOR SETTINGS ----------------
CKEDITOR_UPLOAD_PATH = "uploads/" 

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'extraPlugins': ','.join(['uploadimage', 'image2']),
        'removePlugins': 'image', 
    },
}
