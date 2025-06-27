import createrepo_c
import re


class Parser:
    packages = {}
    packages_graph = {}
    current_package = ''

    @classmethod
    def get_package_graph(cls, pkg_name):
        if not cls.packages:
            cls.parse_packages()

        libs_parents = {} #библиотека: [зависимый_пакет, родительский_пакет]
        libs_childrens = {} #библиотека: пакет

        #Только для нового пакета, при вводе в поиск
        # if pkg_name != cls.current_package:
        #     cls.current_package = pkg_name
        #     libs_parents = {}
        #     libs_childrens = {}
        #     cls.packages_graph = {}
            #При переходе на недалекую вершину не удалять всё, а только ставшие ненужными вершины
        
        #Вынести в отдельные функции без проверки на название для остальных пакетов
        if (pkg_name in cls.packages.keys()):
            
            pkg = cls.packages[pkg_name]
            
            #библиотеки, от которых зависит пакет
            pkg_requires = pkg[0]
            for lib in pkg_requires:
                lib_name = lib[0]
                if lib_name not in libs_parents.keys():
                    libs_parents[lib_name] = []

            #библиотеки, предоставляемые пакетом
            pkg_provides = pkg[1]
            for lib in pkg_provides:
                lib_name = lib[0]
                if lib_name not in libs_childrens.keys():
                    libs_childrens[lib_name] = []
        else:
            return cls.packages_graph
        

        print('\nParents')
        for key in libs_parents.keys():
            print(f'{key}: {libs_parents[key]}')

        # print('\nChildrens')
        # for key in libs_childrens.keys():
        #     print(f'{key}: {libs_childrens[key]}')


        # Добавить обработку библиотек с пробелом в названии
        # for package_name in cls.packages.keys():
        #     for lib in cls.packages[package_name][0]:
        #         lib_name = lib[0]
        #         if ' ' in lib_name:
        #             # print('Нашли необычную библиотеку:')
        #             print(lib_name, package_name)

        #Поиск зависимостей ВВЕРХ
        libs_parents = cls.find_parents_packages(libs_parents, pkg_name)

        #Поиск зависимостей ВНИЗ
        libs_childrens = cls.find_children_packages(libs_childrens, pkg_name)

        # print('\nParents')
        # for key in libs_parents.keys():
        #     print(f'{key}: {libs_parents[key]}')

        # print('\nChildrens')
        # for key in libs_childrens.keys():
        #     print(f'{key}: {libs_childrens[key]}')

        print('\n\n')
        # print(cls.packages_graph)
        
        return cls.packages_graph

    #Парсим нужную информацию о пакетах из определеннго репозитория (по выбору(добавить))
    @classmethod
    def parse_packages(cls):
        repo = 'os'
        repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
        repodata = createrepo_c.Metadata()
        repodata.locate_and_load_xml(repo_url)

        for key in repodata.keys():
            pkg = repodata.get(key)

            pkg_info = [
                pkg.requires,
                pkg.provides,
                pkg.nevra(),
                pkg.version,
                pkg.release,
                pkg.url
            ]
            cls.packages[pkg.name] = pkg_info

        del repodata

    @classmethod
    def find_parents_packages(cls, libs_parents, dependent_package):
        libs = list(libs_parents.keys())
        potential_pkgs = cls.make_potenial_packages(libs_parents)

        i = 0 #индекс для одновременного прохода по списку библиотек и потенциальных пакетов
        while i < len(libs):
            package_name = potential_pkgs[i]
            lib_name = libs[i]
            if (package_name in cls.packages.keys()): #Проверяем есть ли такой пакет в нашем списки пакетов
                provided_libs = list(zip(*cls.packages[package_name][1]))
                if provided_libs and (lib_name in provided_libs[0]):
                    libs_parents[lib_name].append(package_name)
                    cls.packages_graph[package_name] = [dependent_package]
                    libs.remove(lib_name)
                    potential_pkgs.remove(package_name)
                else:
                    i += 1
            else:
                i += 1

        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][1]: #по libs_childrens
                lib_name = lib[0]
                if lib_name in libs:
                    libs_parents[lib_name].append(package_name)
                    if (package_name in cls.packages_graph # существует зависимость от пакета
                        and dependent_package not in cls.packages_graph[package_name]): # значения ещё нет в списке зависимых
                        cls.packages_graph[package_name].append(dependent_package)
                    else:
                        cls.packages_graph[package_name] = [dependent_package]
        return libs_parents
    
    @classmethod
    def find_children_packages(cls, libs_childrens, parent_package):
        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][0]: #по requires
                lib_name = lib[0]
                if lib_name in libs_childrens.keys():
                    libs_childrens[lib_name].append(package_name)
                    if (parent_package in cls.packages_graph # существует зависимость от пакета
                        and package_name not in cls.packages_graph[parent_package]): # значения ещё нет в списке зависимых
                        cls.packages_graph[parent_package].append(package_name)
                    else:
                        cls.packages_graph[parent_package] = [package_name]
        
        return libs_childrens

    #Ищем потенциальные названия пакетов исходя из названия библиотеки
    @staticmethod
    def make_potenial_packages(libs_dict): 
        pkgs = []
        for lib in libs_dict.keys():
            match = re.search(r'^(.+?)(?<=.)(?=[(.]|$)', lib) #все символы до ( или .
            pkg = match.group(1) if match else lib #если не было ( или . то полное название
            if pkg.startswith('('):
                pkg = pkg[1:]
            pkgs.append(pkg)
        
        return pkgs
