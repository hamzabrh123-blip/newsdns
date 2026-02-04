import os
from pathlib import Path
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- DEBUG & SECURITY ---
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-up-halchal-123-aDc-439-082")

ALLOWED_HOSTS = [
    "uttarworld.com", 
    "www.uttarworld.com", 
    ".onrender.com", 
    "localhost", 
    "127.0.0.1",
    "newsdns.onrender.com"
]

# --- SSL & CSRF Fix ---
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

# --- APPS ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
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
                
                # --- NAYE AUTOMATIC PROCESSORS YAHA HAIN ---
                "mynews.context_processors.important_news",
                "mynews.context_processors.site_visits",
                "mynews.context_processors.active_cities_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# --- DATABASE (PC vs Server Switch) ---
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
        )
    }
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- STATIC & MEDIA ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "mynews" / "static"]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret'),
}

# --- CLOUDINARY BLOCK KAR DIYA ---
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media URL ko default rakho
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# --- FACEBOOK & CKEDITOR ---
FB_PAGE_ID = "108286920828619"
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "YOUR_LONG_LIVED_TOKEN_HERE")
CKEDITOR_UPLOAD_PATH = "uploads/" 
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
