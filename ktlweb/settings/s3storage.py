import os

from storages.backends.s3boto import S3BotoStorage
from django.contrib.staticfiles.storage import ManifestFilesMixin


class AWSMedia(ManifestFilesMixin, S3BotoStorage):
    bucket_name = os.environ['AWS_MEDIA']


class AWSStatic(ManifestFilesMixin, S3BotoStorage):
    bucket_name = os.environ['AWS_STATIC']
