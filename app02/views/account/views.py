from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from app02.forms import RegisterForm, SendSmsForm, LoginSmsForm, LoginForm
from app02 import models
from django.db.models import Q
from app02.utils.common import init_user_transaction


def register(request):
    ret = {"status": 1, "msg": ''}
    if request.method == 'POST':
        # 注册请求
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 表单验证通过
            print(form.cleaned_data)
            form.save()
            phone = request.POST.get("phone")
            user = models.UserInfo.objects.filter(phone=phone).first()
            init_user_transaction(user)
            ret["url"] = '/app02/login'
        else:
            # 表单验证失败
            ret["status"] = 0
            ret["msg"] = form.errors
        return JsonResponse(ret)
    else:
        form = RegisterForm()
    return render(request, 'layout/app02/register.html', {'form': form})


def send_sms(request):
    """发送短信"""
    ret = {"status": 1, "msg": ""}
    form = SendSmsForm(request, request.GET)
    if not form.is_valid():
        ret["status"] = 0
        ret["msg"] = form.errors
    return JsonResponse(ret)


def login_sms(request):
    """短信登录"""
    ret = {"status": 1, "msg": ''}
    if request.method == 'POST':
        form = LoginSmsForm(request.POST)
        if form.is_valid():
            # 将用户信息写入session，登录成功之后使用
            user = form.cleaned_data.get('phone')
            request.session['user_id'] = user.id
            request.session['user_name'] = user.username
            # session过期时间要重新设置
            request.session.set_expiry(60*3600*24*7)
            ret['url'] = '/app02/index'
        else:
            ret['status'] = 0
            ret['msg'] = form.errors
        return JsonResponse(ret)
    else:
        form = LoginSmsForm()
    return render(request, "layout/app02/login_sms.html", {"form": form})


def login(request):
    """密码登录"""
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user_obj = models.UserInfo.objects.filter(Q(email=username) | Q(phone=username)).filter(
                password=password).first()
            if not user_obj:
                form.add_error("username", "用户名或密码错误")
            else:
                request.session["user_id"] = user_obj.id
                request.session["user_name"] = user_obj.username
                request.session.set_expiry(3600*24*7)
                return redirect("/app02/index")
        else:
            print(form.errors)
    else:
        form = LoginForm(request)
    return render(request, "layout/app02/login.html", {"form": form})


def get_img(request):
    """生成验证码"""
    from app01.utils.imgcode import check_code
    img, code = check_code()
    print(code)
    # 验证码写入session
    request.session['code'] = code
    request.session.set_expiry(120)
    # 图片写入内存
    from io import BytesIO
    io_obj = BytesIO()
    img.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def logout(request):
    request.session.flush()
    return redirect("/app02/index")


def index(request):
    return render(request, "layout/app02/index.html")
