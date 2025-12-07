import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY/SECRET KEY ----------------
# हमेशा Environment Variable से लें।
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-+lm2ae99@mq!0!4m+663b&^9m3ye(85$$2@(@f=4go(j2m!^ez'
)

# DEBUG को सही Boolean value में बदलना
DEBUG = os.environ.get('DEBUG_VALUE', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "halchal.onrender.com",
]

# Render auto host
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ.get('RENDER_EXTERNAL_HOSTNAME'))


# ---------------- APPS ----------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Static files के लिए आवश्यक
    'django.contrib.staticfiles',

    # Cloudinary और Storage के लिए
    'cloudinary',
    'cloudinary_storage',

    # Your App
    'mynews',

    # CKEditor
    'ckeditor',
    'ckeditor_uploader',
]


# ---------------- MIDDLEWARE ----------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Whitenoise को यहां रखना आवश्यक है
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
# NOTE: Production में Hardcoded credentials को Environment Variables से बदलें।
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL",
            "postgresql://brhnewsdb_user:Wg0XSw1GablPeCkybLFZ1wQ47CfW67M1@dpg-d4oqla7diees73dpqq60-a/brhnewsdb"
        ),
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


# ---------------- GENERAL SETTINGS ----------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------- STATIC FILES ----------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Whitenoise के लिए storage backend
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ---------------- CLOUDINARY AND MEDIA SETTINGS (Images Will Not Be Deleted) ----------------

# Cloudinary credentials को सीधे Environment Variables से लिया जाना चाहिए।
# Note: अगर आप इन्हें ENV variables में सेट करते हैं, तो ये डिफ़ॉल्ट मान हट जाने चाहिए।
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dvoqsrkkq')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '468226887694915')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '1j2X6nWy-0xZqdbr6e9puCVC8VE')

# यह सेटिंग सुनिश्चित करती है कि सभी यूज़र मीडिया (इमेज) सीधे Cloudinary पर सेव हों।
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# ---------------- CKEDITOR SETTINGS ----------------
CKEDITOR_UPLOAD_PATH = "uploads/" 
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_IMAGE_BACKEND = 'cloudinary'

# JQuery URL
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js'


# ---------------- EMAIL ----------------
# NOTE: Production में EMAIL_HOST_PASSWORD भी Environment Variable से लिया जाना चाहिए।
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "hamzabrh@gmail.com"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "your-app-password")
