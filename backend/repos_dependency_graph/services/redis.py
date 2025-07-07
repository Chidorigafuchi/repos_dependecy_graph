import os
import redis
from json import dumps
from hashlib import md5
from typing import List

redis_cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

def make_cache_key(
    session_id: str, 
    pkg_name: str, 
    repos: List[str], 
    extra: str
) -> str:
    """
    Формирует уникальный ключ для кэша Redis на основе параметров:
    сессии, имени пакета и репозиториев.

    Args:
        session_id (str): Идентификатор сессии пользователя.
        pkg_name (str): Имя пакета.
        repos (List[str]): Список репозиториев, в которых ищется пакет.
        extra (str): Префикс, добавляемый к ключу (info: или graph:).

    Returns:
        str: Уникальный строковый ключ для кэширования в Redis.
    """
    key_data = dumps({
        'user_id': session_id,
        'pkg_name': pkg_name,
        'repos': sorted(repos)
    })
    
    return extra + md5(key_data.encode()).hexdigest()