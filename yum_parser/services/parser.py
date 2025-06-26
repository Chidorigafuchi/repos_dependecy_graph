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

        dependecies = {}
        provides = []

        #Только для нового пакета, при вводе в поиск
        # if pkg_name != cls.current_package:
        #     cls.current_package = pkg_name
        #     dependecies = {}
        #     provides = {}
        #     cls.packages_graph = {}
            #При переходе на недалекую вершину не удалять всё, а только ставшие ненужными вершины
        
        #Вынести в отдельные функции без проверки на название для остальных пакетов
        if (pkg_name in cls.packages.keys()):
            
            pkg = cls.packages[pkg_name]
            
            #библиотеки, от которых зависит пакет
            pkg_requires = pkg[0]
            for lib in pkg_requires:
                lib_name = lib[0]
                if lib_name not in dependecies.keys():
                    dependecies[lib_name] = [pkg_name, '']

            #библиотеки, предоставляемые пакетом
            pkg_provides = pkg[1]
            for lib in pkg_provides:
                lib_name = lib[0]
                if lib_name not in provides.keys():
                    provides[lib_name] = pkg_name
        else:
            return cls.packages_graph

        print('\nЗависимости')
        for key in dependecies.keys():
            print(f'{key}: {dependecies[key]}')

        print('\nProvides')
        for key in provides.keys():
            print(f'{key}: {provides[key]}')

        #Добавить обработку библиотек с пробелом в названии
        # for package_name in cls.packages.keys():
        #     for lib in cls.packages[package_name][0]:
        #         lib_name = lib[0]
        #         if ' ' in lib_name:
        #             print('Нашли необычную библиотеку:')
        #             print(lib_name, package_name)


        #Поиск зависимостей ВВЕРХ
        libs = list(dependecies.keys())
        potential_pkgs = cls.make_potenial_packages(dependecies)

        i = 0 #индекс для одновременного прохода по списку библиотек и потенциальных пакетов
        while i < len(libs):
            package_name = potential_pkgs[i]
            lib_name = libs[i]
            if (package_name in cls.packages.keys()): #Проверяем есть ли такой пакет в нашем списки пакетов
                provided_libs = list(zip(*cls.packages[package_name][1]))
                if provided_libs and (lib_name in provided_libs[0]):
                    dependecies[lib_name][1] = package_name
                    cls.packages_graph[package_name] = [dependecies[lib_name][0]]
                    libs.remove(lib_name)
                    potential_pkgs.remove(package_name)
                else:
                    i += 1
            else:
                i += 1

        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][1]: #по provides
                lib_name = lib[0]
                if lib_name in libs:
                    depended_package_name = dependecies[lib_name][0]
                    if (package_name in cls.packages_graph # существует зависимость от пакета
                        and depended_package_name not in cls.packages_graph[provides[lib_name]]): # значения ещё нет в списке зависимых
                        cls.packages_graph[package_name].append(depended_package_name)
                    else:
                        cls.packages_graph[package_name] = [depended_package_name]        

        #Поиск зависимостей ВНИЗ
        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][0]: #по requires
                lib_name = lib[0]
                if lib_name in provides.keys():
                    parent_package_name = provides[lib_name]
                    if (parent_package_name in cls.packages_graph # существует зависимость от пакета
                        and package_name not in cls.packages_graph[parent_package_name]): # значения ещё нет в списке зависимых
                        cls.packages_graph[parent_package_name].append(package_name)
                    else:
                        cls.packages_graph[parent_package_name] = [package_name]

        #Сделать поиск вниз и вверх функциями
        #Для родительских пакетов вызвать поиск вверх
        #Для дочерних поиск вниз

        print('\n\n\n')
        print(cls.packages_graph)
        
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
