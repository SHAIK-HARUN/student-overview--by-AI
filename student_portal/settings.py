"""
Django settings for Student Profile AI Portal
Modern Bootstrap 5 + Chart.js dashboard
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-student-profile-ai-portal-secret-key-2024-xai'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.admin_panel',
]

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

ROOT_URLCONF = 'student_portal.urls'

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

WSGI_APPLICATION = 'student_portal.wsgi.application'

# Database configuration with Serverless/Netlify fallback
# In Netlify functions or AWS Lambda, the root is read-only, so SQLite can reside in /tmp
if os.environ.get('NETLIFY') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    DB_PATH = Path('/tmp') / 'db.sqlite3'
    # Copy pre-seeded database to /tmp if it doesn't exist yet
    if not DB_PATH.exists() and (BASE_DIR / 'db.sqlite3').exists():
        import shutil
        shutil.copyfile(BASE_DIR / 'db.sqlite3', DB_PATH)
else:
    DB_PATH = BASE_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Real SMTP Email Configuration using Gmail
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'shaikashfaq911@gmail.com')
# Gmail App Password (16 characters, e.g. "abcd efgh ijkl mnop")
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'wman clnx uaih gcrt')
DEFAULT_FROM_EMAIL = f"Harun Academic Intelligence <{EMAIL_HOST_USER}>"
SERVER_EMAIL = EMAIL_HOST_USER

# WhatsApp Configuration (College official number)
COLLEGE_WHATSAPP_NUMBER = os.environ.get('COLLEGE_WHATSAPP_NUMBER', '+919182257621')
WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', '')  # Meta WhatsApp Cloud API or Twilio/UltraMsg webhook URL
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')

# Dataset path
DATASETS_CSV = BASE_DIR / 'Datasets.csv'
