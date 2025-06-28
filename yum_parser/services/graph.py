from .parser import parse_packages


class Graph:
    packages = {}
    current_package = ''
    saved_packages_graph = {}

    @classmethod
    def get_package_graph(cls, pkg_name):
        parent_packages = []
        children_packages = []

        if not cls.packages:
            cls.packages = parse_packages()

        if (pkg_name not in cls.packages.keys()):
            return {}
                    
        if pkg_name != cls.current_package:
            cls.current_package = pkg_name
            packages_graph = {
                'package_to_package': {},
                'set_to_package': {},
                'package_to_library': {},
            }
            cls.saved_packages_graph = {}
        else:
            return cls.saved_packages_graph

        parent_packages, packages_graph = cls.get_package_neighbours(pkg_name, packages_graph, up=True)

        children_packages, packages_graph = cls.get_package_neighbours(pkg_name, packages_graph, up=False)

        for package in parent_packages:
            parent_packages, packages_graph = cls.get_package_neighbours(package, packages_graph, up=True)

        for package in children_packages:
            children_packages, packages_graph = cls.get_package_neighbours(package, packages_graph, up=False)

        cls.saved_packages_graph = packages_graph

        return packages_graph
    
    @classmethod
    def get_package_neighbours(cls, current_package, packages_graph, up): #Переименовать
        dependecies = []
        neighbours = []
        pkg = cls.packages[current_package]
        package_dependencies = pkg[0] if up else pkg[1]
        
        for dependency in package_dependencies:
            dependency_name = dependency[0]
            if dependency_name not in dependecies:
                dependecies.append(dependency_name)
        
        neighbours, packages_graph = cls.find_package_neighbours(dependecies, current_package, packages_graph, up)

        return neighbours, packages_graph
    
    @classmethod
    def find_package_neighbours(cls, dependecies, current_package, packages_graph, up):
        neighbours = []
        dependecies_neighbours = {}

        for dependecy_name in dependecies:
            dependecies_neighbours[dependecy_name] = []
        
        for package_name in cls.packages.keys(): 
            package_dependencies = cls.packages[package_name][1] if up else cls.packages[package_name][0]
            for dependecy in package_dependencies:
                dependecy_name = dependecy[0]
                if dependecy_name in dependecies:
                    if package_name not in neighbours:
                        neighbours.append(package_name)
                        dependecies_neighbours[dependecy_name].append(package_name)

        for dependency in dependecies_neighbours.keys():
            packages = dependecies_neighbours[dependency]
            if (packages):
                if up:
                    packages_graph = cls.add_dependence(packages, [current_package], packages_graph)
                else:
                    packages_graph = cls.add_dependence([current_package], packages, packages_graph)
            else:
                if up:
                    if (current_package in packages_graph['package_to_library'].keys()):
                        packages_graph['package_to_library'][current_package].append(dependency)
                    else:
                        packages_graph['package_to_library'][current_package] = [dependency]
        


        return neighbours, packages_graph

    def add_dependence(main_packages, dependent_packages, packages_graph):
        if (len(main_packages) == 1):
            package_name = main_packages[0]
            if (package_name in packages_graph['package_to_package'].keys()):
                for dependent_pkg in dependent_packages:
                    if dependent_pkg not in packages_graph['package_to_package'][package_name]:
                        packages_graph['package_to_package'][package_name].append(dependent_pkg)
            else:
                packages_graph['package_to_package'][package_name] = dependent_packages
        else:
            package_name = 'SET_' + main_packages[0][:-3]
            if (package_name in packages_graph['set_to_package'].keys()):
                packages_graph['set_to_package'][package_name] += dependent_packages
            else:
                packages_graph['set_to_package'][package_name] = dependent_packages
        
        return packages_graph
