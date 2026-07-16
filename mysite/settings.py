import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import json

load_dotenv()

# 1. Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Security Settings
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-key-2026")

ALLOWED_HOSTS = [
    'uttarworld.com',          
    'www.uttarworld.com',      
    '127.0.0.1',             
    'localhost',
]
PREPEND_WWW = False  # Kyunki aap bina www ke site chalana chahte hain
# 3. SSL & CSRF Settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    'https://uttarworld.com',
    'https://www.uttarworld.com',
]

# 4. Apps & Middleware
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
   
    "cloudinary_storage",
    "cloudinary",
    "nested_admin",  
    "shopping",
    "import_export",
    
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

# 5. Templates
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

# 6. DATABASE
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# 7. STATIC & MEDIA SETTINGS
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Agar mynews folder nahi hai toh sirf shopping/static rakhein
STATICFILES_DIRS = [
    BASE_DIR / "shopping" / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ☁️ CLOUDINARY CONFIGURATION
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': os.environ.get("CLOUDINARY_API_KEY"),
    'API_SECRET': os.environ.get("CLOUDINARY_API_SECRET"),
    'AUTO_RENAME_KEY': False,
    'USE_RESOURCE_TYPE_BY_PATH': True,
}

# 8. Storage Logic
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# 9. CKEditor
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

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 11. Internationalization
LANGUAGE_CODE = 'hi'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Google JSON
google_json_str = os.environ.get("GOOGLE_JSON_CONTENT", "{}")
try:
    GOOGLE_JSON_CONTENT = json.loads(google_json_str)
except json.JSONDecodeError:
    GOOGLE_JSON_CONTENT = {}
    print("WARNING: GOOGLE_JSON_CONTENT is not a valid JSON!")

