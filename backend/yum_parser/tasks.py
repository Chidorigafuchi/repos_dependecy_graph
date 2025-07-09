from celery import shared_task
import subprocess
from pickle import loads
from zlib import decompress
from collections import defaultdict
from typing import Dict, Optional, List

from .models import Tracked_package

from .services.graph import get_package_graph
from .services.package_tracking import save_package_snapshot
from .services.parser import repos_union
from repos_dependency_graph.services.redis import redis_get
from .services.parser import parse_repos


@shared_task
def update_tracked_packages() -> Dict[str, int]:
    """
    Задача для Celery
    Проверяет наличие новых вышедших версий у пакетов

    Для каждого уникального набора репозиториев группирует отслеживаемые пакеты,
    загружает информацию о пакетах из Redis, строит графы зависимостей и сохраняет
    снимки с помощью `save_package_snapshot`.

    Возвращает количество успешно обновлённых пакетов.

    Returns:
        Dict[str, int]: Словарь с ключом 'Обновленных пакетов' и числом обновлённых пакетов.
    """
    tracked = Tracked_package.objects.all().order_by('repos_hash')

    updated = 0
    repos_packages = defaultdict(list)

    compressed_info = redis_get('repos_info:compressed')

    if not compressed_info:
        return False
    
    decompressed_info = decompress(compressed_info)
    packages_info = loads(decompressed_info)
    
    for package in tracked:
        repo_paths = [tp_repo.repo for tp_repo in package.tracked_package_repo_set.all()]
        repos = tuple(repo.get_full_url() for repo in repo_paths)
        repos_packages[repos].append(package)
            
    for repos_list in repos_packages.keys():
        print(repos_list)
        group_repos_packages = repos_union(repos_list)

        for package in repos_packages[repos_list]:
            package_name = package.name

            graph = get_package_graph(package_name, repos_list, repos_packages=group_repos_packages)
            info = packages_info.get(package_name)

            new_nevra = save_package_snapshot(
                package, 
                graph, 
                info
            )

            if new_nevra:
                print(f'Обновил пакет - {package_name}')
                updated += 1

    print(f"Обновили {updated} пакетов из {tracked.count()} отслеживаемых.")

    result = {'Обновленных пакетов': updated}

    return result

@shared_task
def parse_repos_task(unloaded_repos: Optional[List[str]] = None) -> None:
    """
    Асинхронно запускает функцию `parse_repos` для парсинга метаданных репозиториев.

    Используется Celery для выполнения задачи в фоне. При необходимости принимает список репозиториев, 
    которые нужно дозагрузить.

    Args:
        unloaded_repos (Optional[List[str]]): Список путей к репозиториям, которые нужно дозагрузить повторно. 
                                              Если не указан, будут загружены все из базы данных.

    Returns:
        None
    """
    parse_repos(unloaded_repos)