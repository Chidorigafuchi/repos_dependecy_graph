from .graph import Graph

def get_package_info(package_name):
    package_info = {}

    if not Graph.packages:
        return package_info

    package_info_list = Graph.packages[package_name]

    obsoletes = get_names(package_info_list[2])
    conflicts = get_names(package_info_list[3])

    package_info = {
        'obsoletes': obsoletes,
        'conflicts': conflicts,
        'nevra': package_info_list[4],
        'version': package_info_list[5],
        'release': package_info_list[6],
        'url': package_info_list[7],
    }

    return package_info


def get_names(dependecies):
    if dependecies:
        dependecies = list(zip(*dependecies))[0]
    return dependecies
