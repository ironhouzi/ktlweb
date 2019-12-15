from storages.backends.s3boto import S3BotoStorage
import os


class AWSMedia(S3BotoStorage):
    bucket_name = os.environ['AWS_MEDIA']


class AWSStatic(S3BotoStorage):
    bucket_name = os.environ['AWS_STATIC']
