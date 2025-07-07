import os
import redis
from json import dumps
from hashlib import md5

redis_cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

def make_cache_key(session_id, pkg_name, repos, extra):
    key_data = dumps({
        'user_id': session_id,
        'pkg_name': pkg_name,
        'repos': sorted(repos)
    })
    
    return extra + md5(key_data.encode()).hexdigest()