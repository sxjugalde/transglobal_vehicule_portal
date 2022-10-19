#!/bin/sh

#wait

cd /app

celery -A vehicle_service_portal worker -l INFO
