from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from app01.forms import RegisterForm, SendSmsForm, LoginSmsForm
from app01 import models
from app01.utils.sms import send_sms_single


def register(request):
    ret = {"status": 1, "msg": ''}
    if request.method == 'POST':
        # 注册请求
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 表单验证通过
            print(form.cleaned_data)
            form.save()
            ret["url"] = 'app01/login'
        else:
            # 表单验证失败
            ret["status"] = 0
            ret["msg"] = form.errors
        return JsonResponse(ret)
    else:
        form = RegisterForm()
    return render(request, 'app01/register.html', {'form': form})


def send_sms(request):
    """发送短信"""
    ret = {"status": 1, "msg": ""}
    form = SendSmsForm(request, request.GET)
    if not form.is_valid():
        ret["status"] = 0
        ret["msg"] = form.errors
    return JsonResponse(ret)


def login_sms(request):
    ret = {"status": 1, "msg": ''}
    if request.method == 'POST':
        form = LoginSmsForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('phone')
            request.session['user_id'] = user.id
            request.session['user_name'] = user.username
            ret['url'] = '/app01/home'
        else:
            ret['status'] = 0
            ret['msg'] = form.errors
        return JsonResponse(ret)
    form = LoginSmsForm()
    return render(request, "app01/login_sms.html", {"form": form})
