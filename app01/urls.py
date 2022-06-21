from django.contrib import admin
from django.urls import path,include
from app01.views.account import views

urlpatterns = [
    # 注册
    path('register/', views.register, name='register'),
    # 发送短信
    path('send/sms/', views.send_sms, name='send_sms'),
    # 短信登录
    path('login/sms/', views.login_sms, name='login_sms'),

]