from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from app01.models import UserInfo
from django.conf import settings
from app01 import models
import datetime


class LoginMiddleware(MiddlewareMixin):

    def process_request(self, request):
        user_id = request.session.get("user_id")
        request.tracer = UserInfo.objects.filter(id=user_id).first()
        """白名单,没有登录的用户都可以访问的url"""
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        if not request.tracer:
            return redirect("/app01/login")

        # 登录成功之后获取额度
        # 方式一：免费额度在数据库中存储
        _object = models.Transaction.objects.filter(user=request.tracer, status=2).order_by("-id").first()
        current_datetime = datetime.datetime.now()
        # 判断是否已过期
        if _object.end_time and _object.end_time<current_datetime:
            _object = models.Transaction.objects.filter(user=request.tracer, status=2).order_by("id").first()
        request.price_policy = _object
