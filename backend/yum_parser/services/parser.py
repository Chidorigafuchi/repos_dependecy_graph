import createrepo_c
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from pickle import dumps, loads
from zlib import compress, decompress
from django.db import DatabaseError
import logging

from yum_parser.models import Repo_path
from repos_dependency_graph.services.redis import redis_get, redis_set
from .reparse_repos import reparse_repos, disable_reparse_repos

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class PackageDependencies:
    requires: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)

@dataclass
class PackageInfo:
    obsoletes: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    nevra: str = ""
    version: str = ""
    release: str = ""
    url: str = ""


def parse_repos(unloaded_repos: List[str] = None) -> None:
    """
    Загружает метаданные пакетов из рпозиториев, которые получает либо как аргумент, либо из базы данных, 
    извлекает зависимости и информацию о пакетах,сериализует и сжимает их, затем сохраняет в Redis кэш на 25 часов.
    Также сохраняет в кэш загруженные пакеты

    Args:
        unloaded_repos (List[str]): Список неудачно загруженных репозиториев

    Redis keys used:
    - 'repos_dependencies:compressed': зависимости пакетов по каждому репозиторию
    - 'repos_info:compressed': основная информация о пакетах (без деления по репозиториям)

    Returns:
        None
    """
    repos_packages_dependencies = {}
    repos_packages_info = {}
    reparsing = False

    if unloaded_repos is not None:
        repos_paths = unloaded_repos.copy()
        reparsing = True
    else:
        try:
            repos_paths = Repo_path.objects.all()
            repos_paths = [repo_url.get_full_url() for repo_url in repos_paths]
        except DatabaseError as e:
            logger.error(f'Ошибка при получении путей репозиториев из базы данных: {e}')
            reparse_repos()
            return
    
    unloaded_repos = []

    for repo_url in repos_paths:
        logger.info(f'Обрабатываю репозиторий {repo_url}')
        try:
            repodata = createrepo_c.Metadata()
            repodata.locate_and_load_xml(repo_url)

            logger.info(f'Успешно загрузил {repo_url}')

            packages_dependencies = {}
            packages_info = {}

            keys = list(repodata.keys())

            for key in keys:
                pkg = repodata.get(key)

                logger.info(f'обрабатываю - {pkg.name}')

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
            logger.warning(f'Неудалось загрузить репозиторий - {repo_url}')
            unloaded_repos.append(repo_url) 
            continue

        repos_packages_dependencies[repo_url] = packages_dependencies
        repos_packages_info.update(packages_info)
    
    if repos_packages_dependencies and repos_packages_info:
        cache_parsed_repos(reparsing, repos_packages_dependencies, repos_packages_info)

        logger.info('Успешно загрузили репозитории')
        if unloaded_repos:
            logger.info(f'Незагруженные репозитории: {unloaded_repos}')
            reparse_repos(unloaded_repos)
        else:
            disable_reparse_repos()
    else:
        logger.error('Ошибка при загрузке репозиториев')
        reparse_repos()


def cache_parsed_repos(
        reparsing: bool, 
        repos_packages_dependencies: Dict[str, Dict[str, PackageDependencies]], 
        repos_packages_info: Dict[str, PackageInfo]
    ) -> None:
    """
    Обновляет и сохраняет в Redis зависимости и информацию о пакетах.

    Если `reparsing=True`, предварительно загружает существующие данные из Redis и объединяет с новыми.

    Args:
        reparsing (bool): Флаг, указывающий, является ли это повторной попыткой парсинга.
        repos_packages_dependencies (Dict[str, Dict[str, PackageDependencies]): Зависимости пакетов по каждому репозиторию.
        repos_packages_info (Dict[str, PackageInfo]): Общая информация о пакетах.

    Returns:
        None
    """
    if reparsing:
        cached_dependencies =loads(decompress(redis_get('repos_dependencies:compressed')))
        cached_info = loads(decompress(redis_get('repos_info:compressed')))
        
        repos_packages_dependencies.update(cached_dependencies)
        repos_packages_info.update(cached_info)

    compressed_dependencies = compress(dumps(repos_packages_dependencies))
    compressed_info = compress(dumps(repos_packages_info))

    redis_set('repos_dependencies:compressed', compressed_dependencies, ex=60 * 60 * 25)
    redis_set('repos_info:compressed', compressed_info, ex=60 * 60 * 25)


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
        from yum_parser.tasks import parse_repos_task
        parse_repos_task.delay()
        
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