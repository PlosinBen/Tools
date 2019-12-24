#!/usr/bin/python3
import sys
sys.path.append(sys.path[0] + "/../..")
import memcache
from .schema import CacheBase

host = '127.0.0.1' #'MEMCACHE_HOST
port = '11211' #MEMCACHE_PORT

class Cache(CacheBase):
    def __init__(self, key, timeout=0):
        super().__init__('memcache', key, timeout)
        self._mem = Memcache()

    def loads(self, default=None):
        super().loads()
        data = self._mem.fetch(self.getKey())
        return default if data is None else data

    def dumps(self, data=None, timeout:int=None):
        super().dumps()
        self._mem.putOrUpdate(self.getKey(), data, self.getTimeout(timeout))

    def clear(self):
        super().clear()
        self._mem.delete(self.getKey())

class Memcache():
    def __init__(self):
        connStr = '{}:{}'.format(host, port)
        self.conn = memcache.Client([connStr], debug=True)

    def fetch(self, key:str):
        return self.conn.get(key)

    def fetchMulti(self, key:list):
        return self.conn.get_multi(key)

    #Add a value if key doesn't exist in the cache
    def put(self, key:str, value:str, timeout:int = 0):
        return self.conn.add(key, value, timeout)

    def putOrUpdate(self, key:str, value:str, timeout:int = 0):
        return self.conn.set(key, value, timeout)

    def putOrUpdateMulti(self, key:str, data:dict={}):
        if len(data) == 0:
            return False
        return self.conn.set_multi(key, data)

    def update(self, key:str, value:str):
        return self.conn.replace(key, value)

    def delete(self, key:str):
        return self.conn.delete(key)

    def deleteMulti(self, keys:list):
        return self.conn.delete_multi(keys)

if __name__ == '__main__':
    import time
    cache = Cache('test')
    cache.dumps( [ 1, (2,), {'B'} ] )
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
