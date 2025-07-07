import createrepo_c
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from pickle import dumps, loads
from zlib import compress, decompress

from repos_dependency_graph.services.redis import redis_cache

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


def parse_packages() -> None:
    """
    Загружает метаданные пакетов из указанных репозиториев, извлекает зависимости и информацию о пакетах,
    сериализует и сжимает их, затем сохраняет в Redis кэш на 25 часов.

    Redis keys used:
    - 'repos_dependencies:compressed': зависимости пакетов по каждому репозиторию
    - 'repos_info:compressed': основная информация о пакетах (без деления по репозиториям)

    Returns:
        None
    """
    repos = ['os', 'updates', 'debuginfo', 'kernel-rt', 'kernel-testing']
    repos_packages_dependencies = {}
    repos_packages_info = {}
    
    for repo in repos:
        repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
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

        repos_packages_dependencies[repo] = packages_dependencies
        repos_packages_info.update(packages_info)

    compressed_dependencies = compress(dumps(repos_packages_dependencies))
    compressed_info = compress(dumps(repos_packages_info))

    redis_cache.set('repos_dependencies:compressed', compressed_dependencies, ex=60 * 60 * 25)
    redis_cache.set('repos_info:compressed', compressed_info, ex=60 * 60 * 25)
    
def repos_union(repos: List[str]) -> Dict[str, PackageDependencies]:
    """
    Объединяет зависимости пакетов из нескольких репозиториев в один словарь.

    Если кэш в Redis недоступен, данные будут заново загружены и сохранены в кэш на 25 часов.

    Args:
        repos (List[str]): Список названий репозиториев.

    Returns:
        Dict[str, PackageDependencies]: Словарь зависимостей по именам пакетов.
    """
    cached_packages_data = redis_cache.get('repos_dependencies:compressed')
    packages = {}
    repos_packages = {}

    if cached_packages_data:
        decompressed_data = decompress(cached_packages_data)
        repos_packages = loads(decompressed_data)
    else:
        parse_packages()
        decompressed_data = decompress(redis_cache.get('repos_dependencies:compressed'))
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