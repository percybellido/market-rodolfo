from .base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mercado_db',
        'USER': 'rodolfo',
        'PASSWORD': 'rodolfosuica890',
        'HOST': 'localhost',
        'PORT': '5432',
    }

}

CSRF_TRUSTED_ORIGINS = [
    "https://domismarket.com",
    "https://www.domismarket.com",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
