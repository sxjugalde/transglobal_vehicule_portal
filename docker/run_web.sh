#!/bin/sh

#wait

cd /app/

#migrate
python manage.py migrate --noinput
python manage.py runserver 0:8000
