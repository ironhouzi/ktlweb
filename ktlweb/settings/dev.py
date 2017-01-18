from .base import *

import sys
from logging import config


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False
# ALLOWED_HOSTS = ['localhost']

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

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

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    }

}

config.dictConfig(LOGGING)

try:
    from .local import *
except ImportError:
    pass
