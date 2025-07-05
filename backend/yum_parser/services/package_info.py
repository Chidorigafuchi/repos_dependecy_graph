from .graph import Graph

class Package_info:
    saved_package_info = {}
    current_package = ''

    @classmethod
    def get_package_info(cls, package_name):
        if cls.current_package == package_name:
            return cls.saved_package_info
        
        package_info = {}

        if not Graph.packages:
            return package_info
        
        cls.current_package = package_name

        package_info_list = Graph.packages[package_name]

        obsoletes = cls.get_names(package_info_list[2])
        conflicts = cls.get_names(package_info_list[3])

        package_info = {
            'obsoletes': obsoletes,
            'conflicts': conflicts,
            'nevra': package_info_list[4],
            'version': package_info_list[5],
            'release': package_info_list[6],
            'url': package_info_list[7],
        }

        cls.saved_package_info = package_info

        return package_info

    def get_names(dependecies):
        if dependecies:
            dependecies = list(zip(*dependecies))[0]
        return dependecies
