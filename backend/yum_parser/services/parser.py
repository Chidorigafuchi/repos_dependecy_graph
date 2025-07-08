import createrepo_c
from dataclasses import dataclass
from typing import Dict, List, Tuple
from pickle import dumps, loads
from zlib import compress, decompress
from django.db import DatabaseError
import logging

from repos_dependency_graph.services.redis import redis_get, redis_set
from yum_parser.models import Repo_path

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class PackageDependencies:
    requires: List[str]
    provides: List[str]

@dataclass
class PackageInfo:
    obsoletes: List[str]
    conflicts: List[str]
    nevra: str
    version: str
    release: str
    url: str


def parse_repos() -> None:
    """
    Загружает метаданные пакетов из указанных репозиториев, извлекает зависимости и информацию о пакетах,
    сериализует и сжимает их, затем сохраняет в Redis кэш на 25 часов. Также сохраняет в кэш загруженные пакеты

    Redis keys used:
    - 'repos_dependencies:compressed': зависимости пакетов по каждому репозиторию
    - 'repos_info:compressed': основная информация о пакетах (без деления по репозиториям)

    Returns:
        None
    """
    repos_packages_dependencies = {}
    repos_packages_info = {}
    unloaded_repos = []

    try:
        repos_paths = Repo_path.objects.all()
        repos_paths = [repo_url.get_full_url() for repo_url in repos_paths]
    except DatabaseError as e:
        logger.error(f'Ошибка при получении путей репозиториев из базы данных: {e}')
        return
    
    for repo_url in repos_paths:
        try:
            repodata = createrepo_c.Metadata()
            repodata.locate_and_load_xml(repo_url)

            packages_dependencies = {}
            packages_info = {}

            keys = list(repodata.keys())

            for key in keys:
                pkg = repodata.get(key)

                packages_dependencies[pkg.name] = PackageDependencies(
                    requires=pkg.requires,
                    provides=pkg.provides
                )

                packages_info[pkg.name] = PackageInfo(
                    obsoletes=get_names(pkg.obsoletes),
                    conflicts=get_names(pkg.conflicts),
                    nevra=pkg.nevra(),
                    version=pkg.version,
                    release=pkg.release,
                    url=pkg.url
                )
                
                repodata.remove(key)
        except Exception as e:
            unloaded_repos.append(repo_url) 
            continue

        repos_packages_dependencies[repo_url] = packages_dependencies
        repos_packages_info.update(packages_info)

    if repos_packages_dependencies and repos_packages_info:
        compressed_dependencies = compress(dumps(repos_packages_dependencies))
        compressed_info = compress(dumps(repos_packages_info))

        redis_set('repos_dependencies:compressed', compressed_dependencies, ex=60 * 60 * 25)
        redis_set('repos_info:compressed', compressed_info, ex=60 * 60 * 25)

        logger.info('Успешно загрузили репозитории')
        if unloaded_repos:
            logger.info(f'Незагруженные репозитории: {unloaded_repos}')
    else:
        logger.error('Ошибка при загрузке репозиториев')


def parse_unloaded_repos(unloaded_repos) -> None:
    """
    Пытается дозагрузить метаданные пакетов из репозиториев, которые не смогли подгрузиться в основной функции.

    Args:
        repos (List[str]): Список репозиториев, с которых не получилось спарсить информацию.

    Redis keys used:
    - 'repos_dependencies:compressed': зависимости пакетов по каждому репозиторию
    - 'repos_info:compressed': основная информация о пакетах (без деления по репозиториям)

    Returns:
        None
    """
    cached_packages_dependencies = redis_get('repos_dependencies:compressed')
    repos_packages_dependencies = decompress(loads(cached_packages_dependencies))
    
    cached_packages_info = redis_get('repos_info:compressed')
    repos_packages_info = decompress(loads(cached_packages_info))    


def repos_union(repos: List[str]) -> Dict[str, PackageDependencies]:
    """
    Объединяет зависимости пакетов из нескольких репозиториев в один словарь.

    Args:
        repos (List[str]): Список названий репозиториев.

    Returns:
        Dict[str, PackageDependencies]: Словарь зависимостей по именам пакетов.
    """
    cached_packages_data = redis_get('repos_dependencies:compressed')
    packages = {}
    repos_packages = {}

    if not cached_packages_data:
        return packages
    
    decompressed_data = decompress(cached_packages_data)
    repos_packages = loads(decompressed_data)
    for repo in repos:
        if repo in repos_packages:
            packages.update(repos_packages[repo])

    return packages


def get_names(dependencies: List[Tuple[str]]) -> List[str]:
    """
    Извлекает имена зависимостей из списка кортежей.

    Args:
        dependencies (List[Tuple[str]]): Зависимости в виде кортежей [(имя, ...), (имя, ...)] .

    Returns:
        List[str]: Список имён зависимостей.
    """
    if dependencies:
        return list(list(zip(*dependencies))[0])
    return []