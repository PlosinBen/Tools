#!/usr/bin/python3
from .schema import CacheBase
import os
import pickle
import time

PATH_ROW = ''

class Cache(CacheBase):
    def __init__(self, key, timeout=0):
        super().__init__('memcache', key, timeout)
        self._path = PATH_RAW + '/cache/'
        if not os.path.exists(self._path):
           os.mkdir(self._path)

    def loads(self, default=None):
        super().loads()
        cachFilePath = self._getCacheFilePath()
        if not os.path.isfile(cachFilePath):
            return default

        cacheData = { 'data': None, 'timeout': 0 }
        with open(cachFilePath, 'rb') as f:
            cacheData = pickle.load(f)
        if cacheData.get('timeout') == 0 or os.stat(cachFilePath).st_mtime + cacheData.get('timeout') > time.time():
            return cacheData.get('data')

        return default

    def dumps(self, data=None, timeout:int=None):
        super().dumps()
        with open(self._getCacheFilePath(), 'wb') as f:
            pickle.dump({
                'data': data,
                'timeout': self.getTimeout(timeout)
            }, f)

    def clear(self):
        super().clear()
        cachFilePath = self._getCacheFilePath()
        if os.path.isfile(cachFilePath):
            os.remove(cachFilePath)

    def _getCacheFilePath(self):
        return self._path + self.getKey() + '.pickle'



if __name__ == '__main__':
    from app import powerDict
    cache = Cache('test')
    cache.dumps( powerDict({'B': 'D'}) )
    data = cache.loads()
    print( type(data) )
    print( data )

    cache.dumps( [ 2, (2,3), {'B': 'D'} ], 5 )
    data = cache.loads()
    print( 'Nor load cache' )
    print( data )

    time.sleep(5)
    data = cache.loads()
    print( 'after timeout load cache' )
    print( data )
