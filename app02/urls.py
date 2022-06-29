from django.urls import path, include
from app02.views.account import views
from app02.views.backend import views2

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
    # 后台管理首页
    path('backend/', views2.backend, name='backend'),
    # 创建项目
    path('create/project/', views2.create_project, name='create_project'),
    # 判断能够继续创建项目
    path('check/eligibility/', views2.eligibility, name='eligibility')
]