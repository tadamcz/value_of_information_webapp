web: gunicorn config.wsgi:application
worker: python manage.py qcluster
release: python manage.py migrate