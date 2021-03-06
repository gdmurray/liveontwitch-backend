"""
Django settings for liveontwitch project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime

DEVELOPMENT_ENV_FILE = ".env"


def set_envfile():
    if os.path.isfile(DEVELOPMENT_ENV_FILE):
        with open(DEVELOPMENT_ENV_FILE) as f:
            os.environ.update(
                line.replace('export ', '', 1).strip().split('=', 1) for line in f
            )


set_envfile()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'Twitter',
    'twitch',

    'storages',
    'rest_framework',
    'oauth2_provider',
    'corsheaders',

]

AUTH_USER_MODEL = "core.User"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'liveontwitch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['core/templates', 'twitch/templates'],
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

WSGI_APPLICATION = 'liveontwitch.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',#os.environ.get('DB_NAME', 'liveontwitch'),
        'HOST': 'postgres-postgresql',  # ,os.environ.get('DB_HOST', 'localhost'),
        'PORT': 5432,
        'USER': 'postgres',  # os.environ.get('DB_USER', 'gregmurray'),
        'PASSWORD': 'LlEGNgq7wt' #os.environ.get('DB_PASS', 'root'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'twitch.backends.OAuth2Backend',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}

AWS_STORAGE_BUCKET_NAME = 'liveontwitch-prod'
AWS_S3_REGION_NAME = 'ca-central-1'  # e.g. us-east-2
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY", )
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", )

# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# you run `collectstatic`).
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SITE_URL = 'api.liveontwitch.app'

TWITCH_AUTH_CLIENT_ID = os.environ.get('TWITCH_AUTH_CLIENT_ID', None)
TWITCH_AUTH_CLIENT_SECRET = os.environ.get('TWITCH_AUTH_CLIENT_SECRET', None)

TWITCH_AUTH_REDIRECT_URI = "https://api.liveontwitch.app/twitch/callback/"

TWITCH_AUTH_CALLBACK_URL = "/twitch/callback/"
TWITCH_AUTH_PROTOCOL = "https://"

TWITCH_SUBSCRIPTION_CALLBACK_URL = os.environ.get("TWITCH_SUBSCRIPTION_CALLBACK_URL", "/twitch/subscription/callback/")
TWITCH_SUBSCRIPTION_KEY = os.environ.get("TWITCH_SUBSCRIPTION_KEY")
TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID", None)
TWITTER_CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET", None)

SESSION_COOKIE_SECURE = False

FRONTEND_URL = "http://localhost:3000"
FRONTEND_CALLBACK = "/callback"

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
ACCESS_TOKEN_EXPIRE_SECONDS = 86400

CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost")

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
