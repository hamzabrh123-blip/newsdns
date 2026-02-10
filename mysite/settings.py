import os
from pathlib import Path
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- DEBUG & SECURITY ---
# Render par DEBUG False hona chahiye, local pe True
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-key-123")

ALLOWED_HOSTS = [
    "uttarworld.com", 
    "www.uttarworld.com", 
    ".onrender.com", 
    "localhost", 
    "127.0.0.1",
    "newsdns.onrender.com"
]

# --- SSL & CSRF Fix (Render Production) ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://uttarworld.com", 
    "https://www.uttarworld.com", 
    "https://newsdns.onrender.com",
    "https://*.onrender.com" 
]

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # Static files handling
    "django.contrib.staticfiles",
    "mynews",
    "ckeditor",
    "ckeditor_uploader",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # WhiteNoise for Static
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
                # Dono functions yahan hain taaki error na aaye
                "mynews.context_processors.site_visits",
                "mynews.context_processors.news_data_processor", 
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# --- DATABASE (SSL FIX FOR RENDER) ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True if not DEBUG else False
    )
}

# --- STATIC & MEDIA ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "mynews" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# File Storage settings (Render delete fix is handled by ImgBB in models)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False

# --- CKEDITOR CONFIG ---
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'height': 300,
        'width': '100%',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Format', 'FontSize', 'TextColor', 'BGColor'],
            ['RemoveFormat', 'Maximize', 'Source']
        ],
        'removePlugins': 'elementspath,resize,flash,smiley,iframe',
    },
}

# --- EMAIL & KEYS ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# API Keys from Environment Variables
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- I18N SETTINGS (Hindi & India Time) ---
LANGUAGE_CODE = 'hi'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True
