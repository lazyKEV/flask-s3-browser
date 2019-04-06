import boto3
from flask import session
import os

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET_ACCESS_KEY')
REGION = os.getenv('REGION')
S3_BUCKET = os.getenv('S3_BUCKET')


def _get_s3_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=REGION
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = S3_BUCKET

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    s3 = _get_s3_resource()
    return s3.meta.client.list_buckets().get('Buckets')
