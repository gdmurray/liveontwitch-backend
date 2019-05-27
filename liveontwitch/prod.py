from .settings import *

SESSION_COOKIE_SECURE = True
ALLOWED_HOSTS = ['backend-server', '159.203.59.206', 'localhost', 'web']

# FRONTEND_URL = "https://liveontwitch.app"
CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
        'PASSWORD': 'postgres'
    }
}
