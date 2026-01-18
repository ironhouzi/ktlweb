from .base import *     # noqa
from .base import KTLWEB_LOGGER, TEMPLATES, TRUTH

import os

from logging import config

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True  # type: ignore

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4q0bwaw+!93b2m-_a)4j%+l5kqi71n!$*1hy(u)_a-08jzea0r'
BASE_DIR = '/opt'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_URL = '/static/'
#
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

# if os.path.isfile('.env'):
#     with open('.env') as f:
#         for line in f.readlines():
#             k, v = line.strip().split('=')
#             os.environ[k] = v

COMPRESS_ENABLED = os.getenv('COMPRESS_ENABLED', 'true').lower() in TRUTH
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-north-1')
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False  # required by wagtail docs
STATIC_URL = os.environ['STATIC_URL']
MEDIA_URL = os.environ['MEDIA_URL']
ALLOWED_HOSTS = ['www.ktl.no', 'localhost', '127.0.0.1', '[::1]']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

gcal_logger = KTLWEB_LOGGER['loggers']['gcal']  # type: ignore
KTLWEB_LOGGER['root'] = gcal_logger  # type: ignore

config.dictConfig(KTLWEB_LOGGER)
