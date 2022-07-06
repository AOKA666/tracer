from django.urls import path
from app01.views.account import views
from app01.views import project

urlpatterns = [
    # 注册
    path('register/', views.register, name='register'),
    # 发送短信
    path('send/sms/', views.send_sms, name='send_sms'),
    # 短信登录
    path('login/sms/', views.login_sms, name='login_sms'),
    # 密码登录
    path('login/', views.login, name='login'),
    # 生成验证码
    path('get/img/', views.get_img, name='get_img'),
    # 网站首页
    path('index/', views.index, name='index'),
    # 退出登录
    path('logout/', views.logout, name='logout'),


    # 项目管理
    path('project/list/', project.project_list, name='project_list') 
]