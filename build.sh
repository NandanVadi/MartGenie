#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
# Migrations are handled by the release phase in Procfile, 
# but if you prefer running them here, uncomment the line below:
# python manage.py migrate
