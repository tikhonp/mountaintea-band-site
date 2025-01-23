#!/bin/bash

python manage.py migrate --noinput
gunicorn --bind 0.0.0.0:8000 --access-logfile - -w 2 mountaintea_band_site.wsgi:application
