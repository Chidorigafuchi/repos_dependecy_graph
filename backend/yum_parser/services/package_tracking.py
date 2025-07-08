import json
from typing import Dict, List
from hashlib import sha1

from .graph import get_package_graph, PackageGraph
from .parser import PackageInfo
from .package_info import get_package_info
from ..models import Tracked_package, Tracked_package_repo, Repo_path, Package_nevra_info


def track_package(session_key: str, package_name: str, repos: List[str]) -> Dict[str, bool]:
    """
    Отслеживает пакет и сохраняет его граф зависимостей и метаинформацию, если он ещё не отслеживался
    с данным набором репозиториев.

    Хэширует отсортированный список репозиториев и использует этот хэш для определения уникальности записи.
    Если отслеживание с таким session_key, именем пакета и repos_hash ещё не существует — создаёт его,
    сохраняет связи с соответствующими объектами `Repo_path`.

    Args:
        session_key (str): Уникальный ключ сессии пользователя.
        package_name (str): Имя пакета, который пользователь хочет отслеживать.
        repos (List[str]): Список URL репозиториев, в которых ищется пакет.

    Returns:
        Dict[str, bool]: Словарь с флагом:
            - `'track_created'`: была ли создана новая запись отслеживания (True/False).
    """
    created_package = False

    all_repo_paths = Repo_path.objects.select_related('base_url').all()

    matching_repo_paths = [
        repo for repo in all_repo_paths
        if repo.get_full_url() in repos
    ]

    if not matching_repo_paths:
        return {'track_created': 'unknown'}
    
    sorted_matching_repo_paths = sorted(matching_repo_paths, key=lambda r: r.get_full_url())
    sorted_repos = sorted(repos)

    repos_hash=sha1(json.dumps(sorted_repos).encode()).hexdigest()

    new_tracked_package, created_package = Tracked_package.objects.get_or_create(
        session_key=session_key,
        name=package_name,
        repos_hash=repos_hash
    )
        
    if not created_package:
        return {'track_created': created_package}
    
    for repo_path in sorted_matching_repo_paths:
        new_tracked_package_repo, created_package_repo = Tracked_package_repo.objects.get_or_create(
            tracked_package=new_tracked_package,
            repo=repo_path,
        )

    graph = get_package_graph(package_name, repos)
    info = get_package_info(package_name)
    new_nevra = save_package_snapshot(
        new_tracked_package, 
        graph, 
        info
    )

    return {'track_created': created_package}


def save_package_snapshot(
        tracked_package: Tracked_package,
        graph: PackageGraph, 
        info: PackageInfo
    ) -> bool:
    """
    Сохраняет НЕВРА пакета и его графа зависимостей, если такой НЕВРА ещё нет в базе.

    Args:
        package_name (str): Имя пакета.
        graph (PackageGraph): Граф зависимостей пакета.
        info (PackageInfo): Объект с информацией о пакете.

    Returns:
        bool: new_nevra — была ли создана новая запись `Package_nevra`
    """
    package_nevra, new_nevra = Package_nevra_info.objects.get_or_create(
        tracked_package=tracked_package,
        nevra=info.nevra,
        defaults={
            'obsoletes': json.dumps(info.obsoletes),
            'conflicts': json.dumps(info.conflicts),
            'graph_json': json.dumps(graph.__dict__)
        }
    )

    return new_nevra