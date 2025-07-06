from .parser import repos_union, get_names
from typing import Dict, List, Tuple, Any
from repos_dependency_graph.services.redis import redis_cache, make_cache_key
from pickle import dumps, loads

MIN_DEPENDENCIES_TO_SET = 5
MAX_NEIGHBOURS = 100

def get_package_graph_with_cache(
    session_key: str,
    pkg_name: str, 
    repos: List[str]
) -> Dict[str, Dict[str, List[str]]]:
    redis_key = make_cache_key(session_key, pkg_name, repos, 'graph:')
    saved_packages_graph = redis_cache.get(redis_key)

    if saved_packages_graph:
        return loads(saved_packages_graph)

    packages_graph = get_package_graph(pkg_name, repos)

    redis_cache.set(redis_key, dumps(packages_graph), ex=60 * 5)

    return packages_graph

def get_package_graph(pkg_name: str, repos: List[str]) -> Dict[str, Dict[str, List[str]]]:
    repos_packages = repos_union(repos)

    if (not repos_packages.get(pkg_name)):
        return {}
                
    parent_packages = []
    children_packages = []
    packages_graph = {
        'package_package': {},
        'set_package': {},
        'library_package': {},
        'sets': {},
    }

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
    repos_packages: Dict[str, List[Any]],
    current_package: str, 
    packages_graph: Dict[str, Dict[str, List[str]]], 
    up: bool
) -> Tuple[List[str], Dict[str, Dict[str, List[str]]]]:
    package_info = repos_packages[current_package]
    package_info_dependencies = package_info['requires'] if up else package_info['provides']
    
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
    repos_packages: Dict[str, List[Any]],
    dependencies: List[str], 
    current_package: str, 
    packages_graph: Dict[str, Dict[str, List[str]]], 
    up: bool
) -> Tuple[List[str], Dict[str, Dict[str, List[str]]]]:
    neighbours = []
    dependencies_neighbours = {}

    for dependecy_name in dependencies:
        dependencies_neighbours[dependecy_name] = []
    
    for package_name in repos_packages.keys(): 
        if up:
            package_info_dependencies = repos_packages[package_name]['provides'] 
        else:
            package_info_dependencies = repos_packages[package_name]['requires']
        
        for dependecy in package_info_dependencies:
            dependecy_name = dependecy[0]
            if dependecy_name in dependencies:
                dependencies_neighbours[dependecy_name].append(package_name)
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
                if (current_package in packages_graph['library_package'].keys()):
                    packages_graph['library_package'][current_package].append(dependency)
                else:
                    packages_graph['library_package'][current_package] = [dependency]

    return neighbours, packages_graph

def add_dependence(
    main_packages: List[str], 
    dependent_packages: List[str], 
    dependency: str, 
    packages_graph: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Dict[str, List[str]]]:
    if (len(main_packages) == 1):
        package_name = main_packages[0]

        if len(dependent_packages) < MIN_DEPENDENCIES_TO_SET:
            if package_package := (packages_graph['package_package'].get(package_name)):
                for dependent_pkg in dependent_packages:
                    if dependent_pkg not in package_package:
                        package_package.append(dependent_pkg)
            else:
                packages_graph['package_package'][package_name] = dependent_packages
        else:
            dependency_name = 'SET_' + dependency
            packages_graph['sets'][dependency_name] = dependent_packages
            if set_package := packages_graph['set_package'].get(package_name):
                set_package.append(dependency_name)
            else:
                packages_graph['set_package'][package_name] = [dependency_name]
    else:
        dependency_name = 'SET_' + dependency
        packages_graph['sets'][dependency_name] = main_packages
        if set_package := packages_graph['set_package'].get(dependency_name):
            set_package += dependent_packages
        else:
            packages_graph['set_package'][dependency_name] = dependent_packages
    
    return packages_graph
