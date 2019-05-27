#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.

exec gunicorn -b 0.0.0.0:8080  liveontwitch.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=liveontwitch.prod \
    --log-level debug --reload
