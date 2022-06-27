import hashlib
from django.conf import settings
from .. import models
from ..models import PriceStrategy
import uuid


def encoder(password):
    """MD5加密"""
    if password:
        hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
        hash_object.update(password.encode('utf-8'))
        return hash_object.hexdigest()


def init_user_transaction(user):
    """初始化为免费用户"""
    models.Transaction.objects.create(
        status=1,
        user=user,
        price=PriceStrategy.objects.filter(name="免费用户").first(),
        payment=0,
        order_num=uuid.uuid4()
    )