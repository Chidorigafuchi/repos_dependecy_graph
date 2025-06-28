import re
from .parser import parse_packages


class Graph:
    packages = {}
    current_package = ''

    @classmethod
    def get_package_graph(cls, pkg_name):
        parent_packages = []
        children_packages = []
        packages_graph = {}

        if not cls.packages:
            cls.packages = parse_packages()

        if (pkg_name in cls.packages.keys()):
            pkg = cls.packages[pkg_name]
            #тут информация о пакете
        else:
            return packages_graph

        if pkg_name != cls.current_package:
            cls.current_package = pkg_name
            packages_graph = {}
        #При переходе на недалекую вершину не удалять всё, а только ставшие ненужными вершины
        
        # Добавить обработку библиотек с пробелом в названии
        # for package_name in cls.packages.keys():
        #     for lib in cls.packages[package_name][0]:
        #         lib_name = lib[0]
        #         if ' ' in lib_name:
        #             # print('Нашли необычную библиотеку:')
        #             print(lib_name, package_name)

        parent_packages, packages_graph = cls.get_package_parents(pkg_name, packages_graph)

        children_packages, packages_graph = cls.get_package_childrens(pkg_name, packages_graph)

        # print('\nРодительские пакеты:\n', parent_packages)

        # print('\nДочерние пакеты:\n', children_packages)

        # print('\n\n')
        # for key in packages_graph.keys():
        #     print(f'{key}: {packages_graph[key]}')

        grand_parent_packages = []

        for package in parent_packages:
            parent_packages, packages_graph = cls.get_package_parents(package, packages_graph)
            grand_parent_packages += parent_packages

        grand_children_packages = []
        for package in children_packages:
            children_packages, packages_graph = cls.get_package_childrens(package, packages_graph)
            grand_children_packages += children_packages

        return packages_graph
    
    @classmethod
    def get_package_parents(cls, pkg_name, packages_graph):
        libs_parents = []
        parent_packages = []
        pkg = cls.packages[pkg_name]
        pkg_requires = pkg[0]
        
        for lib in pkg_requires:
            lib_name = lib[0]
            if lib_name not in libs_parents:
                libs_parents.append(lib_name)
        
        libs_parents, parent_packages, packages_graph = cls.find_parents_packages(libs_parents, pkg_name, packages_graph)

        # print('\nНеиспользоваенные библиотеки родителей:')
        # for lib in libs_parents.keys():
        #     if not libs_parents[lib]:
        #         print(lib)
        
        return parent_packages, packages_graph

    @classmethod
    def get_package_childrens(cls, pkg_name, packages_graph):
        libs_childrens = []
        children_packages = []
        pkg = cls.packages[pkg_name]
        pkg_provides = pkg[1]

        for lib in pkg_provides:
            lib_name = lib[0]
            if lib_name not in libs_childrens:
                libs_childrens.append(lib_name)

        libs_childrens, children_packages, packages_graph = cls.find_children_packages(libs_childrens, pkg_name, packages_graph)

        # print('\nНеиспользоваенные библиотеки детей:')
        # for lib in libs_childrens.keys():
        #     if not libs_childrens[lib]:
        #         print(lib)
        
        return children_packages, packages_graph

    @classmethod
    def find_parents_packages(cls, libs_parents, dependent_package, packages_graph):
        parent_packages = []
        libs_packages = {}

        for lib_name in libs_parents:
            libs_packages[lib_name] = []
        
        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][1]: #по provides
                lib_name = lib[0]
                if lib_name in libs_parents:
                    if package_name not in parent_packages:
                        parent_packages.append(package_name)
                        libs_packages[lib_name].append(package_name)

        for lib in libs_packages.keys():
            packages = libs_packages[lib]
            if (packages):
                packages_graph = cls.add_dependence(packages, [dependent_package], packages_graph)

        return libs_packages, parent_packages, packages_graph
    
    @classmethod
    def find_children_packages(cls, libs_childrens, parent_package, packages_graph):
        children_packages = []
        libs_packages = {}

        for lib_name in libs_childrens:
            libs_packages[lib_name] = []

        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][0]: #по requires
                lib_name = lib[0]
                if lib_name in libs_childrens:
                    if package_name not in children_packages:
                        children_packages.append(package_name)
                        libs_packages[lib_name].append(package_name)
                
        for lib in libs_packages.keys():
            packages = libs_packages[lib]
            if (packages):
                packages_graph = cls.add_dependence([parent_package], packages, packages_graph)

        return libs_packages, children_packages, packages_graph

    def add_dependence(main_packages, dependent_packages, packages_graph):
        if (len(main_packages) == 1):
            package_name = main_packages[0]
            if (package_name in packages_graph):
                for dependent_pkg in dependent_packages:
                    if dependent_pkg not in packages_graph[package_name]:
                        packages_graph[package_name].append(dependent_pkg)
            else:
                packages_graph[package_name] = dependent_packages
        else:
            package_name = 'SET_' + main_packages[0]
            if (package_name in packages_graph):
                packages_graph[package_name] += dependent_packages
            else:
                packages_graph[package_name] = dependent_packages
        
        return packages_graph
