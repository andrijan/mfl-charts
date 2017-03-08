release: python fiver/manage.py migrate
release: python fiver/manage.py populate_data
web: gunicorn config.wsgi:application
