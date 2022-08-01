import json
import os
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
from sts.sts import Sts

secret_id = settings.TENCENT_COS_SECRET_ID 
secret_key = settings.TENCENT_COS_SECRET_KEY


def create_bucket(bucket_name, region='ap-shanghai'):

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    client.create_bucket(
        Bucket=bucket_name,
        ACL='public-read'
    )

    # 设置CORS
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'POST', 'HEAD', 'DELETE'],
                'AllowedHeader': '*',
                'ExposeHeader': '*',
                'MaxAgeSeconds': 500
            }
        ]
    }
    response = client.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration=cors_config
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


def cos_delete_file(bucket, file_list, region='ap-shanghai'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    # 构造批量删除的字典格式
    delete = []
    for file in file_list:
        delete.append({file.key:file})
    response = client.delete_objects(
        Bucket=bucket,
        Delete={
            'Object': delete,
            'Quiet': 'true'
        }
    )


def get_credential(bucket, region='ap-shanghai'):
        config = {
            'url': 'https://sts.tencentcloudapi.com/',
            # 域名，非必须，默认为 sts.tencentcloudapi.com
            'domain': 'sts.tencentcloudapi.com', 
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,
            'secret_id': secret_id,
            # 固定密钥
            'secret_key': secret_key,
            # 设置网络代理
            # 'proxy': {
            #     'http': 'xx',
            #     'https': 'xx'
            # },
            # 换成你的 bucket
            'bucket': bucket,
            # 换成 bucket 所在地区
            'region': region,
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': '*', 
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
            'allow_actions': [
                # 简单上传
                'name/cos:PutObject',
            ],
        }
        sts = Sts(config)
        response = sts.get_credential()
        return response


def delete_bucket(bucket, region='ap-shanghai'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    # 删除桶中所有的文件

    while True:
        obj_list = client.list_objects(Bucket=bucket)
        print(obj_list.get("Contents"))
        if not obj_list.get("Contents"):
            break
        # 'Contents': [{
        # 'Key': '1658564360647-a5.jpeg', 
        # 'LastModified': '2022-07-23T08:19:19.000Z', 
        # 'ETag': '"b674a2f906abb67f2260efa81d2e8296"', 
        # 'Size': '26009', 'Owner': {'ID': '1307733527', 
        # 'DisplayName': '1307733527'}, 
        # 'StorageClass': 'STANDARD'},]
        contents = obj_list.get("Contents")
        client.delete_objects(
            Bucket=bucket,
            Delete={
                'Object': [{'Key': item['Key']} for item in contents],
                'Quiet': 'true'
            }
        )
    # 删除bucket
    client.delete_bucket(
        Bucket=bucket
    )