release: python manage.py makemigrations && python manage.py migrate
web: gunicorn config.wsgi:application
worker: python manage.py qcluster
