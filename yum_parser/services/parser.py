import createrepo_c

class Parser:
    packages = {}
    dependecies = {}
    provides = {}
    packages_graph = {}

    @classmethod
    def get_package_graph(cls, pkg_name):
        if not cls.packages:
            cls.parse_packages()

        main_pkg_info = {
        'name': 'unkn',
        'nevra': 'unkn',
        'version': 'unkn',
        'release': 'unkn',
        'url': 'unkn',
        }

        if (pkg_name in cls.packages.keys()):
            pkg = cls.packages[pkg_name]

            main_pkg_info = {
                'name': pkg_name,
                'nevra': pkg[2],
                'version': pkg[3],
                'release': pkg[4],
                'url': pkg[5],
            }
            
            #добавляем библиотеки, от которых зависит искомый пакет без пакетов
            pkg_requires = pkg[0]
            for lib in pkg_requires:
                lib_name = lib[0]
                if lib_name not in cls.dependecies.keys():
                    cls.dependecies[lib_name] = ''

            #добавляем библиотеки, предоставляемые искомым пакетом
            pkg_provides = pkg[1]
            for lib in pkg_provides:
                lib_name = lib[0]
                if lib_name not in cls.provides.keys():
                    cls.provides[lib_name] = pkg_name
        else:
            return cls.packages_graph

        print(cls.dependecies)
        print(cls.provides)

        for package_name in cls.packages.keys(): 
            for lib in cls.packages[package_name][0]:
                lib_name = lib[0]
                if lib_name in cls.provides.keys():
                    if (cls.provides[lib_name] in cls.packages_graph # существует зависимость от пакета
                        and package_name not in cls.packages_graph[cls.provides[lib_name]]): # значения ещё нет в списке зависимых
                        cls.packages_graph[cls.provides[lib_name]].append(package_name)
                    else:
                        cls.packages_graph[cls.provides[lib_name]] = [package_name]

        print('\n\n\n')
        print(cls.packages_graph)
        
        return cls.packages_graph

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

    