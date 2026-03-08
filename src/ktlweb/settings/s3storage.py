from storages.backends.s3boto3 import S3Boto3Storage
import os


class AWSMedia(S3Boto3Storage):
    bucket_name = os.environ['AWS_MEDIA']
    querystring_auth = True


class AWSStatic(S3Boto3Storage):
    bucket_name = os.environ['AWS_STATIC']
    default_acl = 'public-read'
    querystring_auth = False
