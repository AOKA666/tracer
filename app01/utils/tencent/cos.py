from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings


secret_id = settings.TENCENT_COS_SECRET_ID 
secret_key = settings.TENCENT_COS_SECRET_KEY


def create_bucket(bucket_name, region='ap-shanghai'):

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    response = client.create_bucket(
        Bucket=bucket_name,
        ACL='public-read'
    )


def cos_upload_file(bucket, file_obj, file_name, region='ap-shanghai'):
    region = 'ap-shanghai'
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Key=file_name,
        Body=file_obj,
    )
    return f'https://{bucket}.cos.{region}.myqcloud.com/{file_name}'
