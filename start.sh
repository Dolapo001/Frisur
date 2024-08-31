#!/bin/sh
docker-compose up
exec gunicorn --bind 0.0.0.0:8000 --timeout 0 barbing_salon.wsgi:application
