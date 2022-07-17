import hashlib
from django.conf import settings
import uuid


def encoder(password):
    """MD5加密"""
    if password:
        hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
        hash_object.update(password.encode('utf-8'))
        return hash_object.hexdigest()


def uid(string):
    data = "{}-{}".format(uuid.uuid4(), string)
    return encoder(data)