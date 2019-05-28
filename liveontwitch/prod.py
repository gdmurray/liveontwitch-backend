from .settings import *

SESSION_COOKIE_SECURE = True
ALLOWED_HOSTS = ['api.liveontwitch.app']

FRONTEND_URL = "https://liveontwitch.app"
CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'liveontwitchdb'),
        'USER': os.environ.get('DB_USER', 'greg'),
        'HOST': 'postgres-service',  # os.environ.get('DB_HOST', 'localhost'),
        'PORT': 5432,
        'PASSWORD': os.environ.get('DB_PASS', 'uG9Gn6TQdSBbv9FOJETFnICbdCKlp57f')
    }
}
"""
