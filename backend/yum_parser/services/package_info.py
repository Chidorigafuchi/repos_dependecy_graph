from .graph import Graph

def get_package_info(package_name):
    package_info = {}

    if not Graph.packages:
        return package_info

    package_info_list = Graph.packages[package_name]

    package_info = {
        'obsoletes': package_info_list[2],
        'conflicts': package_info_list[3],
        'nevra': package_info_list[4],
        'version': package_info_list[5],
        'release': package_info_list[6],
        'url': package_info_list[7],
    }

    return package_info
