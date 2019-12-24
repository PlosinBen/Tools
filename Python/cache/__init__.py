from .file import Cache as fileCache
from .memcache import Cache as MemcacheCache

from .memcache import Memcache

def factory(key, timeout=0, cache:str='memcache'):
    usableCache = {
        'file': fileCache,
        'memcache': MemcacheCache
    }
    if cache in usableCache:
        return usableCache[cache](key=key, timeout=timeout)