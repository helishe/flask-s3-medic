import boto3
from medicalapp.config import S3_KEY, S3_SECRET
from flask import session
from celery import Celery


def _get_s3_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')


def get_bucket(username):
    s3_resource = _get_s3_resource()
    bucket = username.lower() + '-flask-s3-medic'

    return s3_resource.Bucket(bucket)


def create_user_bucket(username):
    s3 = boto3.client('s3')
    bucket = username.lower() + '-flask-s3-medic'
    return s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={
        'LocationConstraint': 'us-east-2'},)


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_presigned_url(bucket_name, object_name, expiration=3600, http_method=None):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration,
                                                    HttpMethod=http_method)
    return response
