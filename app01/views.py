from django.shortcuts import render, HttpResponse, redirect
from app01.forms import RegisterForm
from app01 import models
from app01.utils.sms import send_code


def register(request):
    if request.is_ajax():
        # 发送验证码的请求
        send_code()
        return HttpResponse('ok')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data.pop("confirm_pwd")
            data.pop("code")
            print(data)
            return HttpResponse("验证通过")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})