#!/usr/bin/env bash
set -e

python manage.py migrate --no-input
python manage.py seed_content
python manage.py collectstatic --no-input
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
