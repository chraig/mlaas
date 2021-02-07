# -*- coding: utf-8 -*-
import json
import numbers
import pickle
import redis
from typing import Dict, List, Optional, Type


class StaticDict:
    values: dict = {}


class Channel:
    def __init__(self, name: str, redis_channel: str):
        self._name = name
        self._redis_channel = redis_channel
        self._msg_list = []

    def get_channel(self) -> Dict:
        return {self._name: self._redis_channel}

    def get_msgs(self) -> list:
        return self._msg_list

    def add_msg(self, msg):
        if isinstance(msg, dict) or isinstance(msg, list):
            msg = json.dumps(msg)
        if isinstance(msg, numbers.Number) or callable(msg):
            msg = str(msg)
        self._msg_list.append(msg)
        return msg

    def publish(self, r: redis.Redis):
        for msg in self._msg_list:
            r.publish(self._redis_channel, msg)
        self._msg_list = []


class RedisClient:
    values: dict = {}

    def __new__(cls, host, port, db, channels=None, evt=None):
        obj = super(RedisClient, cls).__new__(cls)

        h = cls._create_redis_key(host, port, db)
        if h not in cls.values:
            cls.values[h] = redis.Redis(host=host, port=port, db=db)

        return obj

    def __init__(self, host, port, db):
        h = self._create_redis_key(host, port, db)
        self.r = self.values[h]

    @staticmethod
    def _create_redis_key(host, port, db):
        return "h={}p={}db={}".format(host, port, db)


class RedisPickleClient(RedisClient):
    def get_pickle(self, key) -> object:
        b = self.r.get(key)
        if b:
            return pickle.loads(b)
        else:
            return {}

    def set_pickle(self, key, value: object) -> Optional[bool]:
        b = pickle.dumps(value)
        return self.r.set(key, b)

    def delete_pickle(self, key):
        try:
            self.r.delete(key)
        except Exception as ex:
            raise


class RedisMessagesClient(RedisClient):
    def __init__(self, host, port, db, channels, evt):
        super().__init__(host=host, port=port, db=db)
        self._channels = channels
        self._evt = evt
        self._channel_handles = ()
        for channel in self._channels:
            self._channel_handles = self._channel_handles\
                                    + (Channel(name=channel, redis_channel=self._channels[channel]),)

    def push(self, channel: Channel, msg: str):
        return channel.add_msg(self._evt["task-id"] + " - " + msg)

    def publish(self):
        for channel in self._channels:
            channel.publish(self.r)
