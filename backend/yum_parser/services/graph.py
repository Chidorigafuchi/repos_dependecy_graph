from .parser import parse_packages
from typing import Dict, List, Tuple

class Graph:
    packages = {}
    current_package = ''
    saved_packages_graph = {}
    used_repos = []
    MIN_DEPENDENCIES_TO_SET = 5
    MAX_NEIGHBOURS = 100

    @classmethod
    def get_package_graph(
        cls, 
        pkg_name: str, 
        repos: List[str]
    ) -> Dict[str, Dict[str, List[str]]]:
        if not cls.packages:
            cls.packages = parse_packages(cls.packages, repos)
            cls.used_repos = repos
            if not cls.packages:
                return {}
            
        if repos != cls.used_repos:
            deleted_repos = [old_repo for old_repo in cls.used_repos if old_repo not in repos]
            if not deleted_repos:
                new_repos = [new_repo for new_repo in repos if new_repo not in cls.used_repos]
                cls.packages = parse_packages(cls.packages, new_repos)
                cls.used_repos += new_repos
            else:
                cls.packages = parse_packages({}, repos)
                cls.used_repos = repos

        if (not cls.packages.get(pkg_name)):
            return {}
                    
        if pkg_name != cls.current_package:
            cls.current_package = pkg_name
            parent_packages = []
            children_packages = []
            packages_graph = {
                'package_package': {},
                'set_package': {},
                'library_package': {},
                'sets': {},
            }
            cls.saved_packages_graph = {}
        else:
            return cls.saved_packages_graph

        parent_packages, packages_graph = cls.get_package_neighbours(pkg_name, packages_graph, up=True)

        children_packages, packages_graph = cls.get_package_neighbours(pkg_name, packages_graph, up=False)

        if len(parent_packages) < cls.MAX_NEIGHBOURS:
            for package in parent_packages:
                _, packages_graph = cls.get_package_neighbours(package, packages_graph, up=True)
        
        if len(children_packages) < cls.MAX_NEIGHBOURS:
            for package in children_packages:
                _, packages_graph = cls.get_package_neighbours(package, packages_graph, up=False)

        cls.saved_packages_graph = packages_graph

        return packages_graph
    
    @classmethod
    def get_package_neighbours(
        cls, 
        current_package: str, 
        packages_graph: Dict[str, Dict[str, List[str]]], 
        up: bool
    ) -> Tuple[List[str], Dict[str, Dict[str, List[str]]]]:
        dependencies = []
        neighbours = []
        package_info = cls.packages[current_package]
        package_info_dependencies = package_info[0] if up else package_info[1]
        
        for dependency in package_info_dependencies:
            dependency_name = dependency[0]
            if dependency_name not in dependencies:
                dependencies.append(dependency_name)
        
        neighbours, packages_graph = cls.find_package_neighbours(dependencies, current_package, packages_graph, up)

        return neighbours, packages_graph
    
    @classmethod
    def find_package_neighbours(
        cls, 
        dependencies: List[str], 
        current_package: str, 
        packages_graph: Dict[str, Dict[str, List[str]]], 
        up: bool
    ) -> Tuple[List[str], Dict[str, Dict[str, List[str]]]]:
        neighbours = []
        dependencies_neighbours = {}

        for dependecy_name in dependencies:
            dependencies_neighbours[dependecy_name] = []
        
        for package_name in cls.packages.keys(): 
            package_info_dependencies = cls.packages[package_name][1] if up else cls.packages[package_name][0]
            for dependecy in package_info_dependencies:
                dependecy_name = dependecy[0]
                if dependecy_name in dependencies:
                    dependencies_neighbours[dependecy_name].append(package_name)
                    if package_name not in neighbours:
                        neighbours.append(package_name)

        for dependency in dependencies_neighbours.keys():
            packages = dependencies_neighbours[dependency]
            if (packages):
                if up:
                    packages_graph = cls.add_dependence(packages, [current_package], dependency, packages_graph)
                else:
                    packages_graph = cls.add_dependence([current_package], packages, dependency, packages_graph)
            else:
                if up:
                    if (current_package in packages_graph['library_package'].keys()):
                        packages_graph['library_package'][current_package].append(dependency)
                    else:
                        packages_graph['library_package'][current_package] = [dependency]

        return neighbours, packages_graph

    @classmethod
    def add_dependence(
        cls,
        main_packages: List[str], 
        dependent_packages: List[str], 
        dependency: str, 
        packages_graph: Dict[str, Dict[str, List[str]]]
        ) -> Dict[str, Dict[str, List[str]]]:
        if (len(main_packages) == 1):
            package_name = main_packages[0]

            if len(dependent_packages) < cls.MIN_DEPENDENCIES_TO_SET:
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
                    set_package = [dependency_name]
        else:
            dependency_name = 'SET_' + dependency
            packages_graph['sets'][dependency_name] = main_packages
            if set_package := packages_graph['set_package'].get(dependency_name):
                set_package += dependent_packages
            else:
                set_package = dependent_packages
        
        return packages_graph

        