from pickle import dumps, loads
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from repos_dependency_graph.services.redis import redis_cache, make_cache_key
from .parser import repos_union, get_names, PackageDependencies

MIN_DEPENDENCIES_TO_SET = 5
MAX_NEIGHBOURS = 100

@dataclass
class PackageGraph:
    """
    Структура для хранения графа зависимостей пакета.

    Атрибуты:
        package_package (Dict[str, List[str]]): 
            Прямые зависимости между пакетами. 
            Ключ — имя пакета, значение — список зависимых от него пакетов.

        set_package (Dict[str, List[str]]): 
            Отображение групп зависимостей (SET_...) на пакеты. 
            Используется для агрегирования большого количества зависимостей под одним именем.

        library_package (Dict[str, List[str]]): 
            Зависимости, которые не удалось сопоставить с имеющимися пакетами в репозиториях. 

        sets (Dict[str, List[str]]): 
            Содержимое SET-зависимостей
    """
    package_package: Dict[str, List[str]] = field(default_factory=dict)
    set_package: Dict[str, List[str]] = field(default_factory=dict)
    library_package: Dict[str, List[str]] = field(default_factory=dict)
    sets: Dict[str, List[str]] = field(default_factory=dict)

def get_package_graph_with_cache(
        session_key: str, 
        pkg_name: str, 
        repos: List[str]
    ) -> PackageGraph:
    """
    Получает граф зависимостей пакета, используя Redis-кеш.

    Если граф по пакету уже сохранен в Redis — возвращается он.
    Если графа нет — вызывается `get_package_graph`, результат сохраняется в Redis на 5 минуту.

    Args:
        session_key (str): Идентификатор сессии пользователя.
        pkg_name (str): Имя пакета.
        repos (List[str]): Список репозиториев.

    Returns:
        PackageGraph: Граф зависимостей пакета.
    """
    redis_key = make_cache_key(session_key, pkg_name, repos, 'graph:')
    saved_packages_graph = redis_cache.get(redis_key)

    if saved_packages_graph:
        return loads(saved_packages_graph)

    packages_graph = get_package_graph(pkg_name, repos)

    redis_cache.set(redis_key, dumps(packages_graph), ex=60 * 5)

    return packages_graph

def get_package_graph(
        pkg_name: str, 
        repos: List[str], 
        repos_packages: Optional[Dict[str, PackageDependencies]] = {}
    ) -> PackageGraph:
    """
    Строит граф зависимостей для заданного пакета из указанных репозиториев.
    Если pkg_name отсутствует, возвращается пустой PackageGraph

    Args:
        pkg_name (str): Имя пакета.
        repos (List[str]): Список репозиториев.
        repos_packages (Optional[Dict[str, PackageDependencies]]): Готовые данные о пакетах по repos.

    Returns:
        PackageGraph: Построенный граф зависимостей.
    """
    packages_graph = PackageGraph()
    
    if not repos_packages:
        repos_packages = repos_union(repos)

    if (not repos_packages.get(pkg_name)):
        return packages_graph
                
    parent_packages = []
    children_packages = []

    parent_packages, packages_graph = get_package_neighbours(
        repos_packages, 
        pkg_name, 
        packages_graph, 
        up=True
    )

    children_packages, packages_graph = get_package_neighbours(
        repos_packages, 
        pkg_name, 
        packages_graph, 
        up=False
    )

    if len(parent_packages) < MAX_NEIGHBOURS:
        for package in parent_packages:
            _, packages_graph = get_package_neighbours(
                repos_packages, 
                package, 
                packages_graph, 
                up=True
            )
    
    if len(children_packages) < MAX_NEIGHBOURS:
        for package in children_packages:
            _, packages_graph = get_package_neighbours(
                repos_packages, 
                package, 
                packages_graph, 
                up=False
            )

    return packages_graph

def get_package_neighbours(
    repos_packages: Dict[str, PackageDependencies],
    current_package: str, 
    packages_graph: PackageGraph, 
    up: bool
) -> Tuple[List[str], PackageGraph]:
    """
    Получает нужные для поиска соседей зависимости у искомого пакета 

    Args:
        repos_packages (Dict[str, PackageDependencies]): Информация о пакетах из репозиториев.
        current_package (str): Текущий пакет.
        packages_graph (PackageGraph): Текущий граф зависимостей.
        up (bool): 
            True — искать пакеты, от которых зависит текущий (родительские)
            False — искать пакеты, которые зависят от текущего (дочерние)
    Returns:
        Tuple[List[str], PackageGraph]: Найденные соседи и обновлённый граф.
    """
    package_info = repos_packages[current_package]
    package_info_dependencies = package_info.requires if up else package_info.provides
    
    dependencies = get_names(package_info_dependencies)
    
    neighbours, packages_graph = find_package_neighbours(
        repos_packages, 
        dependencies, 
        current_package, 
        packages_graph, 
        up
    )

    return neighbours, packages_graph

def find_package_neighbours(
    repos_packages: Dict[str, PackageDependencies],
    dependencies: List[str], 
    current_package: str, 
    packages_graph: PackageGraph, 
    up: bool
) -> Tuple[List[str], PackageGraph]:
    """
    Находит соседей по зависимостям и обновляет граф.

    Args:
        repos_packages (Dict[str, PackageDependencies]): Все пакеты с зависимостями из репозиториев.
        dependencies (List[str]): Имена зависимостей.
        current_package (str): Пакет, для которого ищутся связи.
        packages_graph (PackageGraph): Граф зависимостей.
        up (bool): True — искать зависимости, False — искать зависящие.

    Returns:
        Tuple[List[str], PackageGraph]: Найденные пакеты и обновлённый граф.
    """
    neighbours = []
    dependencies_neighbours = {}

    for dependency_name in dependencies:
        dependencies_neighbours[dependency_name] = []
    
    for package_name in repos_packages.keys(): 
        if up:
            package_info_dependencies = repos_packages[package_name].provides
        else:
            package_info_dependencies = repos_packages[package_name].requires
        
        for dependency in package_info_dependencies:
            dependency_name = dependency[0]
            if dependency_name in dependencies:
                dependencies_neighbours[dependency_name].append(package_name)
                if package_name not in neighbours:
                        neighbours.append(package_name)

    for dependency in dependencies_neighbours.keys():
        found_neighbours = dependencies_neighbours[dependency]
        if (found_neighbours):
            if up:
                packages_graph = add_dependence(
                    found_neighbours, 
                    [current_package], 
                    dependency, 
                    packages_graph
                )
            else:
                packages_graph = add_dependence(
                    [current_package], 
                    found_neighbours, 
                    dependency, 
                    packages_graph
                )
        else:
            if up:
                if (current_package in packages_graph.library_package.keys()):
                    packages_graph.library_package[current_package].append(dependency)
                else:
                    packages_graph.library_package[current_package] = [dependency]

    return neighbours, packages_graph

def add_dependence(
    main_packages: List[str], 
    dependent_packages: List[str], 
    dependency: str, 
    packages_graph: PackageGraph
    ) -> PackageGraph:
    """
    Добавляет зависимость в граф.

    Args:
        main_packages (List[str]): Основные пакеты (дающие зависимость).
        dependent_packages (List[str]): Зависимые пакеты.
        dependency (str): Имя зависимости.
        packages_graph (PackageGraph): Граф зависимостей.

    Returns:
        PackageGraph: Обновлённый граф.
    """
    if (len(main_packages) == 1):
        package_name = main_packages[0]

        if len(dependent_packages) < MIN_DEPENDENCIES_TO_SET:
            if package_package := (packages_graph.package_package.get(package_name)):
                for dependent_pkg in dependent_packages:
                    if dependent_pkg not in package_package:
                        package_package.append(dependent_pkg)
            else:
                packages_graph.package_package[package_name] = dependent_packages
        else:
            dependency_name = 'SET_' + dependency
            packages_graph.sets[dependency_name] = dependent_packages
            if set_package := packages_graph.set_package.get(package_name):
                set_package.append(dependency_name)
            else:
                packages_graph.set_package[package_name] = [dependency_name]
    else:
        dependency_name = 'SET_' + dependency
        packages_graph.sets[dependency_name] = main_packages
        if set_package := packages_graph.set_package.get(dependency_name):
            set_package += dependent_packages
        else:
            packages_graph.set_package[dependency_name] = dependent_packages
    
    return packages_graph
