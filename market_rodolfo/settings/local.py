from .base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

STATIC_URL = 'static/'
STATICFILES_DIRS=[BASE_DIR/'static']

MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
