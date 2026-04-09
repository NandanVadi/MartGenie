release: python manage.py migrate
web: gunicorn martgenie.wsgi:application --log-file - --access-logfile -
