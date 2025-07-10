import os
import redis
from json import dumps
from hashlib import md5
from typing import List
import logging


logger = logging.getLogger(__name__)

redis_cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

def redis_get(key: str):
    """
    Безопасно получает значение из Redis по заданному ключу.

    Если при получении значения возникает ошибка Redis, она логируется и возвращается None.

    Args:
        key (str): Ключ, по которому нужно получить значение из Redis.

    Returns:
        Optional[bytes]: Значение, полученное из Redis (в виде bytes), или None при ошибке.
    """
    try:
        return redis_cache.get(key)
    except redis.RedisError as e:
        logger.error(f"Ошибка Redis при получении ключа '{key}': {e}")
        return None


def redis_set(key: str, value, ex: int = None):
    """
    Безопасно устанавливает значение в Redis по заданному ключу.

    Если при установке значения возникает ошибка Redis, она логируется и возвращается False.

    Args:
        key (str): Ключ, по которому сохранить значение.
        value (Any): Значение, которое нужно сохранить (обычно bytes или str).
        ex (Optional[int]): Время жизни ключа в секундах (TTL). По умолчанию — None (без истечения срока).

    Returns:
        bool: True, если установка прошла успешно, иначе False.
    """
    try:
        redis_cache.set(key, value, ex=ex)
        return True
    except redis.RedisError as e:
        logger.error(f"Ошибка Redis при установке ключа '{key}': {e}")
        return False


def redis_expire_extend(key: str, extra_seconds: int) -> None:
    """
    Продлевает TTL (время жизни) ключа Redis на указанное количество секунд,
    если у ключа уже есть положительный TTL.

    Args:
        key (str): Ключ Redis.
        extra_seconds (int): Сколько секунд прибавить к текущему TTL.
    """
    ttl = redis_cache.ttl(key)
    if ttl and ttl > 0:
        redis_cache.expire(key, ttl + extra_seconds)


def make_cache_key(
    session_id: str, 
    pkg_name: str, 
    repos: List[str], 
    extra: str = ''
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