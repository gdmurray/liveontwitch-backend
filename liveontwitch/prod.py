from .settings import *

SESSION_COOKIE_SECURE = True
ALLOWED_HOSTS = ['api.liveontwitch.app']

FRONTEND_URL = "https://liveontwitch.app"
CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
