from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liveontwitch.prod')

from django.apps import apps

# Create celery instance
app = Celery('liveontwitch')

# get broker + backend settings from main settings file
app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass