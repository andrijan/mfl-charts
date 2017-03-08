import dj_database_url

from .common import *  # noqa

ALLOWED_HOSTS = env.list(  # noqa
    'DJANGO_ALLOWED_HOSTS',
    default=['fiver-dynasty.herokuapp.com']
)
INSTALLED_APPS += ("gunicorn", )  # noqa

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)  # noqa
