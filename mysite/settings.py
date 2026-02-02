import os
from pathlib import Path
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-up-halchal-123-aDc-439-082")

# Local testing ke liye ise True rakha hai
DEBUG = False

ALLOWED_HOSTS = [
    "uttarworld.com", 
    "www.uttarworld.com", 
    ".onrender.com", 
    "localhost", 
    "127.0.0.1"
]

# --- APPS ---
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
]

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
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ---------------- DATABASE ----------------
DATABASES = {
    'default': dj_database_url.config(
        # Render par ye variable automatically uthaya jayega
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}

# SSL/Connection errors se bachne ke liye ye zaroori hai
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}


# --- LOCALIZATION ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA CONFIG ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Folder check: mynews/static ke andar logo/css rakho
STATICFILES_DIRS = [BASE_DIR / "mynews" / "static"]

# Render par deployment ke liye storage
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CKEDITOR CONFIG ---
CKEDITOR_UPLOAD_PATH = "uploads/" 
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"