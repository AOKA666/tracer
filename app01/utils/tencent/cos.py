from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings


secret_id = settings.TENCENT_COS_SECRET_ID 
secret_key = settings.TENCENT_COS_SECRET_KEY

def create_bucket(bucket_name):
    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
       # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
    region = 'ap-shanghai'      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    response = client.create_bucket(
        Bucket=bucket_name,
        ACL = 'public-read'
    )


def cos_upload_file(bucket):
    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    region = 'ap-shanghai'      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    response = client.upload_file(
        Bucket=bucket,
        Key='p1.jpg',
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )
    print(response['ETag'])