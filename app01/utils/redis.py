from tracer.local_settings import REDIS
import redis


def connect():
    return redis.Redis(host=REDIS['HOST'],
                       port=REDIS['PORT'],
                       password=REDIS['PASSWORD'],
                       encoding='utf8')