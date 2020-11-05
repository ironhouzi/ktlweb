from storages.backends.s3boto3 import S3Boto3Storage
import os


class AWSMedia(S3Boto3Storage):
    bucket_name = os.environ['AWS_MEDIA']


class AWSStatic(S3Boto3Storage):
    bucket_name = os.environ['AWS_STATIC']
    access_key = os.environ['NEW_AWS_ACCESS_KEY_ID']
    secret_key = os.environ['NEW_AWS_SECRET_ACCESS_KEY']
