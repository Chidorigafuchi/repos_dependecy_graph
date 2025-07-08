from typing import Dict, List, Union, Optional
from pickle import dumps, loads
from zlib import decompress
import logging

from .parser import PackageInfo
from repos_dependency_graph.services.redis import redis_set, redis_get, make_cache_key

logger = logging.getLogger(__name__)


def get_package_info(package_name: str) -> Optional[PackageInfo]:
    """
    Извлекает информацию о пакете из глобального кэша Redis, содержащего данные по всем пакетам.

    Args:
        package_name (str): Имя пакета, информацию о котором нужно получить.

    Returns:
        PackageInfo: Дата-класс с информацией о пакете, либо None, если пакет не найден.
    """
    compressed_data = redis_get('repos_info:compressed')
    package_info = PackageInfo()
    
    if not compressed_data:
        from yum_parser.tasks import parse_repos_task
        parse_repos_task.delay()
        
        return package_info
    
    decompressed_data = decompress(compressed_data)
    cached_packages_info = loads(decompressed_data)

    package_info = cached_packages_info.get(package_name)

    return package_info


def get_package_info_with_cache(session_key: str, package_name: str) -> Dict[str, Union[str, List[str]]]:
    """
    Получает информацию о пакете, используя кэш Redis для ускорения повторных запросов.

    Если данные по пакету уже сохранены в Redis — возвращаются они.
    Если данных нет — вызывается `get_package_info`, результат сохраняется в Redis на 1 минуту.

    Args:
        session_key (str): Уникальный ключ сессии пользователя (используется в генерации ключа Redis).
        package_name (str): Имя интересующего пакета.

    Returns:
        Dict[str, Union[str, List[str]]]: Словарь с информацией о пакете.
    """
    redis_key = make_cache_key(session_key, package_name, [], 'info:')
    saved_packages_info = redis_get(redis_key)

    if saved_packages_info:
        return loads(saved_packages_info)
    
    package_info = get_package_info(package_name).__dict__

    redis_set(redis_key, dumps(package_info), ex=60 * 1)

    return package_info


