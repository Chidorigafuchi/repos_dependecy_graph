from typing import Dict, List, Tuple
from django.db import DatabaseError
from collections import defaultdict
from hashlib import sha1
from json import dumps
import logging

from ..models import Tracked_package, Package_nevra_info
from .graph import get_package_graph_with_cache, PackageGraph
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def get_package_versions(session_key: str, pkg_name: str, repos: List[str]) -> List[str]:
    if not session_key or not pkg_name or not repos:
        return []
        
    sorted_repos = sorted(repos)
    repos_hash=sha1(dumps(sorted_repos).encode()).hexdigest()

    try:
        tracked_package = Tracked_package.objects.get(
            session_key=session_key, 
            name=pkg_name, 
            repos_hash=repos_hash
        )
        candidates = Package_nevra_info.objects.filter(tracked_package=tracked_package)
    except Tracked_package.DoesNotExist:
        return []
    except DatabaseError as e:
        logger.error(f'Ошибка при добавлении отслеживаемого пакета в БД: {e}')
        return []

    package_nevras = []
    
    for package_nevra in candidates:
        package_nevras.append(package_nevra.nevra)

    return package_nevras


def get_package_version_diff(session_key: str, pkg_name: str, repos: List[str], nevra: str):
    if not session_key or not pkg_name or not repos or not nevra:
        return {}
        
    sorted_repos = sorted(repos)
    repos_hash=sha1(dumps(sorted_repos).encode()).hexdigest()

    try:
        tracked_package = Tracked_package.objects.get(
            session_key=session_key, 
            name=pkg_name, 
            repos_hash=repos_hash
        )
        package_nevra = Package_nevra_info.objects.get(
            tracked_package=tracked_package,
            nevra=nevra
        )
        package_saved_graph = package_nevra.get_graph()
    except Tracked_package.DoesNotExist:
        return {}
    except Package_nevra_info.DoesNotExist:
        return {}
    except DatabaseError as e:
        logger.error(f'Ошибка при добавлении отслеживаемого пакета в БД: {e}')
        return {}
    
    package_actual_graph = get_package_graph_with_cache(session_key, pkg_name, repos)

    if package_saved_graph == package_actual_graph:
        return {}
    else:
        calculate_graph_diff(package_saved_graph, package_actual_graph)


    result = {
        'package_package': {
            'groonga': ['aboba'],
            'groonga-http': ['test1', 'test2']
        },
        'sets': {
            'glibc_langpack': ['new']
        },
    }

    return result

def calculate_graph_diff(old_graph: PackageGraph, new_graph: PackageGraph):
    print('очень скоро добавится')

    