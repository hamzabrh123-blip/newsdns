import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+lm2ae99@mq!0!4m+663b&^9m3ye(85$$2@(@f=4go(j2m!^ez'

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "mysite-1-kg2r.onrender.com",
]

# ---------------- STATIC ----------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ---------------- MEDIA (local fallback) ----------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Whitenoise
WHITENOISE_ROOT = MEDIA_ROOT
WHITENOISE_USE_FINDERS = True

# Render auto-domain
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ.get('RENDER_EXTERNAL_HOSTNAME'))

# ---------------- APPS ----------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # Your App
    'mynews',

    # CKEditor
    'ckeditor',
    'ckeditor_uploader',
]

# ---------------- CLOUDINARY SETTINGS ----------------
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dvoqsrkkq',
    'API_KEY': '468226887694915',
    'API_SECRET': '1j2X6nWy-0xZqdbr6e9puCVC8VE',  # ← your real secret
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ---------------- MIDDLEWARE ----------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

# ---------------- TEMPLATES ----------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# ---------------- DATABASE ----------------
DATABASES = {
    'default': dj_database_url.config(
        default="postgresql://brhnewsdb_user:Wg0XSw1GablPeCkybLFZ1wQ47CfW67M1@dpg-d4oqla7diees73dpqq60-a/brhnewsdb",
        conn_max_age=600
    )
}

# ---------------- PASSWORD VALIDATION ----------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "hamzabrh@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"

# ---------------- CKEDITOR ----------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_ALLOW_NONIMAGE_FILES = False
