from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Use plain static files (no compression) during development
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

# Print emails to console instead of sending
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
