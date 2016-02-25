from .base import *

import os


DEBUG = os.environ.get('DEBUG', 'False') in ('True',)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', 'True') in ('True',)
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
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() in ('true', '1',)

ADMINS = (
    ('Robin Skahjem-Eriksen', 'robinds@gmail.com'),
)

SERVER_EMAIL = 'webmaster@ktl.no'

# Search

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch',
        'URLS': [os.environ['BONSAI_URL']],
    }
}

try:
    from .local import *
except ImportError:
    pass
