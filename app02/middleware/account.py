from django.utils.deprecation import MiddlewareMixin
from app02.models import UserInfo


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get("user_id")
        request.tracer = UserInfo.objects.filter(id=user_id).first()