release: python fiver/manage.py migrate; python fiver/manage.py populate_data
web: gunicorn fiver.wsgi:application
