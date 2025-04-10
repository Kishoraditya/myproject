from .base import *

DEBUG = os.getenv("DEBUG", "False") == "True"

# Use local storage for Docker
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Configure storage for static files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Allow all hosts in Docker
ALLOWED_HOSTS = ["*"]

# Security settings for Docker (less strict)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False 