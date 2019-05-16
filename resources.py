import boto3
from flask import session
import os
import traceback

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET_ACCESS_KEY')
REGION = os.getenv('REGION')
S3_BUCKET = os.getenv('S3_BUCKET')
EXPIRY_TIME = 5*60


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


def _get_s3_client():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=REGION
        )
    except:     # noqa
        traceback.print_exc()

    return s3_client


def get_presigned_url(s3client, image_path: str):
    url = s3client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': image_path
        },
        ExpiresIn=EXPIRY_TIME
    )

    return url


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
