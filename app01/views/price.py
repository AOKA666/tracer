import datetime
import json

from django.shortcuts import render, redirect

from app01 import models
from app01.utils.common import encoder, uid


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
    print(context)
    return render(request, 'app01/payment.html', {'context': context})


def payment(request, price_policy_id):
    """确认支付"""
    price_policy = models.PricePolicy.objects.get(id=price_policy_id)
    total = request.GET.get("total_balance")
    number = request.GET.get("number")
    if not number.isdecimal():
        return redirect("app01:price")
    if int(number) < 1:
        return redirect("app01:price")
    order = encoder(uid(request.tracer.phone))
    models.Transaction.objects.create(
        status=2,
        order=order,
        user=request.tracer,
        price_policy=price_policy,
        count=number,
        price=total
    )
    url = ""
    params = {
        'app_id': '',
        'method': 'alipay.trade.page.pay',
        'format': 'JSON',
        'return_url': '',
        'notity_url': '',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'biz_content': json.dumps({
            'out_trade_no': order,
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'total_amount': total,
            'subject': 'tracer套餐购买'
        }, separators=(',', ':'))
    }

    
    return redirect(url)