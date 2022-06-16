import random
from app01.utils.redis import connect


def send_code():
    code = random.randint(1000, 9999)
    print(code)
    # 建立连接
    conn = connect()
    # 设置键值
    conn.set('code', code, 60)