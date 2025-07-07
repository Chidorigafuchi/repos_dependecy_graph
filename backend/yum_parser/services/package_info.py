from typing import Dict, List, Union 
from pickle import dumps, loads
from zlib import decompress

from repos_dependency_graph.services.redis import redis_cache, make_cache_key


def get_package_info_with_cache(session_key: str, package_name: str) -> Dict[str, Union[str, List[str]]]:
    redis_key = make_cache_key(session_key, package_name, [], 'info:')
    saved_packages_info = redis_cache.get(redis_key)

    if saved_packages_info:
        return loads(saved_packages_info)
    
    package_info = get_package_info(package_name).__dict__
 
    redis_cache.set(redis_key, dumps(package_info), ex=60 * 1)

    return package_info
def get_package_info(package_name: str) -> Dict[str, Union[str, List[str]]]:
    decompressed_data = decompress(redis_cache.get('repos_info:compressed'))
    cached_packages_info = loads(decompressed_data)

    package_info = cached_packages_info.get(package_name)

    return package_info


