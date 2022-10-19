#!/bin/sh

#wait

cd /app/

#migrate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --bind :8000 --workers 2 customs_app.wsgi:application
