import datetime
import json

from django.shortcuts import render, redirect, HttpResponse
from django_redis import get_redis_connection
from app01 import models
from app01.utils.common import encoder, uid
from app01.utils.alipay.instant_pay import Alipay
from tracer import local_settings


def price(request):
    price_policy_list = models.PricePolicy.objects.filter(category=2)
    return render(request, "app01/price.html", {"price_policy_list": price_policy_list})


def buy(request, price_policy_id):
    """点击购买套餐"""
    price_policy = models.PricePolicy.objects.get(id=price_policy_id)
    number = request.GET.get("number")
    if not number.isdecimal():
        return redirect("app01:price")
    if int(number) < 1:
        return redirect("app01:price")
    # 判断当前用户的价格策略，确定实际支付价格
    current_policy = request.price_policy.price_policy
    if current_policy.category == 1:
        # 是免费版，实际支付费用就是套餐价格
        remaining_balance = price_policy.price * int(number)
        refund_balance = 0
    else:
        # 是收费用户
        # 套餐时间
        duration = request.price_policy.end_time - request.price_policy.start_time
        # 已使用原套餐的时间
        cost_timedelta = (datetime.datetime.now() - request.price_policy.start_time).days
        if cost_timedelta == 0:
            # 当天买了就更换套餐，这天的钱不退
            cost_timedelta = 1
        refund_balance = request.price_policy.price / duration * (duration-cost_timedelta)
        remaining_balance = price_policy.price*int(number) - refund_balance
    context = {
        "policy_id": price_policy_id,
        "policy_name": price_policy.title,
        "policy_price": price_policy.price,
        "number": number,
        "original_balance": int(number)*price_policy.price,
        "subtract_balance": round(refund_balance, 2),
        "total_balance": remaining_balance
    }
    # 写入redis
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.phone)
    conn.set(key, json.dumps(context), ex=60*30)
    return render(request, 'app01/payment.html', {'context': context})


def payment(request, price_policy_id):
    """确认支付"""
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect("app01:price")
    context = json.loads(context_string.decode("utf-8"))

    order = encoder(uid(request.tracer.phone))
    models.Transaction.objects.create(
        status=1,
        order=order,
        user=request.tracer,
        price_policy_id=context['policy_id'],
        count=context['number'],
        price=context['total_balance']
    )
    # 签名生成支付链接并跳转
    alipay = Alipay(
        app_id = local_settings.ALI_APPID,
        return_url = local_settings.RETURN_URL,
        notify_url = local_settings.NOTIFY_URL,
        private_key = local_settings.APP_PRIVATE_KEY_PATH,
        ali_public_key = local_settings.ALI_PUBLIC_KEY_PATH,
    )
    result = alipay.sign(order, context['total_balance'])
    pay_url = "{}?{}".format(local_settings.GATE_WAY_URL, result)
    return redirect(pay_url)


def notify(request):
    return HttpResponse("success")


def pay_return(request):
    # 写入数据库
    params = request.GET.dict()
    sign = params.pop("sign", None)
    alipay = Alipay(
            app_id = local_settings.ALI_APPID,
            return_url = local_settings.RETURN_URL,
            notify_url = local_settings.NOTIFY_URL,
            private_key = local_settings.APP_PRIVATE_KEY_PATH,
            ali_public_key = local_settings.ALI_PUBLIC_KEY_PATH,
        )    
    status = alipay.verify(params, sign)
    if status:
        current_datetime = datetime.datetime.now()
        out_trade_no = params['out_trade_no']
        _object = models.Transaction.objects.filter(order=out_trade_no).first()

        _object.status = 2
        _object.start_time = current_datetime
        _object.end_time = current_datetime + datetime.timedelta(days=365 * _object.count)
        _object.save()
        return HttpResponse('<h1>支付成功</h1>')         