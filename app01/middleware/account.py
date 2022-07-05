from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from app01.models import UserInfo
from django.conf import settings


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get("user_id")
        request.tracer = UserInfo.objects.filter(id=user_id).first()
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        if not request.tracer:
            return redirect("/app01/login")