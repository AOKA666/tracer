import random
from django_redis import get_redis_connection


# def send_code():
#     code = random.randint(1000, 9999)
#     print(code)
#     # 建立redis连接
#     conn = get_redis_connection("default")
#     # 设置键值
#     conn.set('code', code, 60)


from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from tracer.local_settings import SMS_APP_ID, SMS_APP_KEY


def send_sms_single(phone_num, template_id, template_param_list):
    """
    单条发送短信
    :param phone_num: 手机号
    :param template_id: 腾讯云短信模板ID
    :param template_param_list: 短信模板所需参数列表，例如:【验证码：{1}，描述：{2}】，则传递参数 [888,666]按顺序去格式化模板
    :return:
    """
    # appid = SMS_APP_ID  # 自己应用ID
    # appkey = SMS_APP_KEY  # 自己应用Key
    # sms_sign = "动物行为故事与科普"  # 自己腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）
    # sender = SmsSingleSender(appid, appkey)
    # try:
    #     response = sender.send_with_param(86, phone_num, template_id, template_param_list, sign=sms_sign)
    # except HTTPError as e:
    #     response = {'result': 1000, 'errmsg': "网络异常发送失败"}
    # return response

    response = {'result': 0}
    return response