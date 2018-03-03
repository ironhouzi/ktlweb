from .base import TEMPLATES, BASE_DIR, TRUTH
from .base import *     # noqa

import os
import sys
import logging

from logging import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('WAGTAIL_DEBUG', 'False').lower() in TRUTH
# DEBUG = False
# ALLOWED_HOSTS = ['localhost']

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True  # type: ignore

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4q0bwaw+!93b2m-_a)4j%+l5kqi71n!$*1hy(u)_a-08jzea0r'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Search

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch',
        'URLS': [os.getenv('ES_URL', 'http://localhost:9200')],
    }
}

KTLWEB_LOGGER = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(levelname)s - (%(pathname)s:%(lineno)d) %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'detailed'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': logging.DEBUG
    }
}

config.dictConfig(KTLWEB_LOGGER)
