from django.contrib import admin
from django.urls import path,include
from app01.views.account import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('send/sms/', views.send_sms, name='send_sms'),
]