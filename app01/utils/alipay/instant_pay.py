import json
import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from urllib.parse import quote_plus
from base64 import encodebytes, decodebytes


class Alipay:
    def __init__(self,app_id, return_url, notify_url, private_key, ali_public_key,):
        self.app_id = app_id
        self.return_url = return_url
        self.notify_url = notify_url
        self.private_key_path = private_key
        with open(self.private_key_path) as fp:
            self.private_key = RSA.importKey(fp.read())
        self.ali_public_key_path = ali_public_key
        with open(self.ali_public_key_path) as fp:
            self.ali_public_key = RSA.importKey(fp.read())

    def sign(self, order_num, amount):
        """生成支付链接"""
        params = {
            'app_id': self.app_id,
            'method': 'alipay.trade.page.pay',
            'format': 'JSON',
            'return_url': self.return_url,
            'notity_url': self.notify_url,
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps({
                'out_trade_no': order_num,
                'product_code': 'FAST_INSTANT_TRADE_PAY',
                'total_amount': amount,
                'subject': 'tracer套餐购买'
            }, separators=(',', ':'))
        }
        unsigned_string = '&'.join(["{}={}".format(x, params[x]) for x in sorted(params)])
        # SHA256编码
        private_key = self.private_key
        signer = PKCS1_v1_5.new(private_key)
        signature = signer.sign(SHA256.new(unsigned_string.encode('utf-8')))
        # base64编码
        sign_string = encodebytes(signature).decode('utf8').replace('\n', '')
        result = "&".join(["{}={}".format(k, quote_plus(params[k])) for k in sorted(params)])
        result = result + '&sign=' + quote_plus(sign_string)      
        return result

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.ali_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)
        