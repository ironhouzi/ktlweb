from .base import *     # noqa
from .base import TRUTH, KTLWEB_LOGGER

import os

from logging import config

from elasticsearch import RequestsHttpConnection

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in TRUTH
COMPRESS_ENABLED = os.getenv('COMPRESS_ENABLED', 'true').lower() in TRUTH
SECRET_KEY = os.environ['SECRET_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
STATIC_URL = os.environ['STATIC_URL']
MEDIA_URL = os.environ['MEDIA_URL']
STATICFILES_STORAGE = 'ktlweb.settings.s3storage.AWSStatic'
DEFAULT_FILE_STORAGE = 'ktlweb.settings.s3storage.AWSMedia'
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_HOST_USER = os.getenv(
    'SENDGRID_USERNAME',
    os.getenv('EMAIL_HOST_USER', '')
)
EMAIL_HOST_PASSWORD = os.getenv(
    'SENDGRID_PASSWORD',
    os.getenv('EMAIL_HOST_PASSWORD', '')
)
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() in TRUTH

ADMINS = (
    ('Robin Skahjem-Eriksen', 'robindse@gmail.com'),
)

SERVER_EMAIL = 'webmaster@ktl.no'
DEFAULT_FROM_USER = SERVER_EMAIL

# Search
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': os.environ['WAGTAIL_SEARCH_BACKEND'],
        'URLS': [os.environ['BONSAI_URL']],
        'INDEX': 'wagtail',
        'OPTIONS': {
            'connection_class': RequestsHttpConnection,
            'use_ssl': True,
            'verify_certs': False
        }
    }
}

KTLWEB_LOGGER['formatters']['detailed']['format'] = (   # type: ignore
    '%(asctime)s - [%(levelname)s] - (%(pathname)s:%(lineno)d) %(message)s'
)

config.dictConfig(KTLWEB_LOGGER)
