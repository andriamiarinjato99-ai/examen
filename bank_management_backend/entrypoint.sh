#!/bin/sh
set -e
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput
python manage.py seed_demo 2>/dev/null || true
python manage.py collectstatic --noinput 2>/dev/null || true
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60
