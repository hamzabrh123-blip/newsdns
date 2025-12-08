import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "your-secret-key"
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # your apps
    'mynews',

    # rich text editor
    'ckeditor',
    'ckeditor_uploader',

    # cloudinary
    'cloudinary',
    'cloudinary_storage',
]

MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'YOUR_CLOUD_NAME',
    'API_KEY': 'YOUR_API_KEY',
    'API_SECRET': 'YOUR_API_SECRET',
}
