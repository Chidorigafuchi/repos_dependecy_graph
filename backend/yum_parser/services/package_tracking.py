import json
from typing import Dict, List

from .graph import get_package_graph, PackageGraph
from .parser import PackageInfo
from .package_info import get_package_info
from ..models import Tracked_package, Package_nevra, Package_repos_graph


def track_package(session_key: str, package_name: str, repos: List[str]) -> Dict[str, bool]:
    """
    Отслеживает пакет и сохраняет его граф зависимостей и метаинформацию, если он ещё не отслеживался.

    Проверяет, существует ли уже запись для данного `session_key`, `package_name` и отсортированного `repos`.
    Если нет — создает её, а также сохраняет снимок текущей версии пакета и его графа.

    Args:
        session_key (str): Уникальный ключ сессии пользователя.
        package_name (str): Имя пакета для отслеживания.
        repos (List[str]): Список репозиториев, в которых ищется пакет.

    Returns:
        Dict[str, bool]: Словарь с флагом:
            - `'track_created'`: была ли создана новая запись отслеживания;
    """
    created = False    
    sorted_repos = sorted(repos)
    
    obj, created = Tracked_package.objects.get_or_create(
        session_key=session_key,
        name=package_name,
        repos=json.dumps(sorted_repos)
    )
    
    if created:
        graph = get_package_graph(package_name, sorted_repos)
        info = get_package_info(package_name)
        new_nevra, new_graph = save_package_snapshot(package_name, sorted_repos, graph, info)

    return {'track_created': created}


def save_package_snapshot(
        package_name: str, 
        repos: List[str], 
        graph: PackageGraph, 
        info:PackageInfo
    ) -> bool:
    """
    Сохраняет НЕВРА пакета и его графа зависимостей, если такой НЕВРА ещё нет в базе.

    Args:
        package_name (str): Имя пакета.
        repos (List[str]): Список репозиториев, откуда был построен граф.
        graph (PackageGraph): Граф зависимостей пакета (структура зависит от реализации `get_package_graph`).
        info (PackageInfo): Объект с информацией о пакете.

    Returns:
        Tuple[bool, bool]: Кортеж:
            - new_nevra — была ли создана новая запись `Package_nevra`;
            - new_graph — была ли создана новая запись `Package_repos_graph`.
    """
    new_graph = False

    package_nevra, new_nevra = Package_nevra.objects.get_or_create(
        name=package_name,
        nevra=info.nevra,
        defaults={
            'obsoletes': json.dumps(info.obsoletes),
            'conflicts': json.dumps(info.conflicts),
        }
    )

    if new_nevra:
        package_graph, new_graph = Package_repos_graph.objects.get_or_create(
            package_nevra=package_nevra,
            repos=json.dumps(repos),
            defaults={
                'graph_json': json.dumps(graph)
            }
        )

    return new_nevra, new_graph