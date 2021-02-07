# -*- coding: utf-8 -*-
from redis_client import RedisPickleClient


class RedisHandler:
    def __init__(self, redis_host: str, redis_port: int, redis_db: int = 0):
        self._h = "h={}p={}db={}".format(redis_host, redis_port, redis_db)
        self._redis_pickle = RedisPickleClient(host=redis_host, port=redis_port, db=redis_db)

    def get_state(self, key):
        return self._redis_pickle.get_pickle(key)

    def set_state(self, key, value):
        return self._redis_pickle.set_pickle(key, value)

    def delete_state(self, key):
        return self._redis_pickle.delete_pickle(key)
