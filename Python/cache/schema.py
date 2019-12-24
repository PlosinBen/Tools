#!/usr/bin/python3

class CacheBase():
    def __init__(self, name, key, timeout):
        self._name = name
        self._key = key
        self._timeout = timeout

    def loads(self, default=None):
        print('Loading cache from {}'.format(self._key))

    def dumps(self, data=None, timeout:int=None):
        print('Saving cache from {}'.format(self._key))

    def clear(self):
        print('Clear cache from {}'.format(self._key))

    def getKey(self):
        return self._key

    def getTimeout(self, timeout=None):
        return self._timeout if timeout is None else timeout