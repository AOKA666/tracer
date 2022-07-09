from django.urls import path, re_path, include
from app01.views.account import views
from app01.views import project
from app01.views import manage

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
    path('project/list/', project.project_list, name='project_list'),
    # 星标项目
    re_path(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.star, name='star'),
    # 取消星标
    re_path(r'^project/cancel/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.cancel_star, name='cancel_star'),

    # 进入项目
    re_path(r'^manage/(?P<project_id>\d+)/', include([
        re_path(r'^dashboard/$', manage.dashboard, name='dashboard'),
        re_path(r'^issues/$', manage.issues, name='issues'),
        re_path(r'^statistics/$', manage.statistics, name='statistics'),
        re_path(r'^file/$', manage.file, name='file'),
        re_path(r'^wiki/$', manage.wiki, name='wiki'),
        re_path(r'^settings/$', manage.settings, name='settings'),
    ]))
]