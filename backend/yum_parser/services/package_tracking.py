from .graph import Graph
from .package_info import Package_info
from ..models import Tracked_package, Package_nevra, Package_repos_graph
from json import dumps
from typing import Dict, List, Optional


def track_package(session_key: str, package_name: str, repos: List[str]) -> Optional[Dict[str, bool]]:
    created = False
    new = False

    if  Graph.packages.get(package_name):
        obj, created = Tracked_package.objects.get_or_create(
            session_key=session_key,
            name=package_name,
            repos=dumps(repos)
        )
        
        if created:
            new_nevra, new_graph = save_package_snapshot(package_name, repos)

    return {'track_created': created, 'version_created': new_nevra}

def save_package_snapshot(package_name: str, repos: List[str]) -> bool:
    info = Package_info.get_package_info(package_name)
    graph_data = Graph.get_package_graph(package_name, repos)

    new_graph = False

    package_nevra, new_nevra = Package_nevra.objects.get_or_create(
        name=package_name,
        nevra=info['nevra'],
        defaults={
            'obsoletes': dumps(info['obsoletes']),
            'conflicts': dumps(info['conflicts']),
        }
    )

    package_graph, new_graph = Package_repos_graph.objects.get_or_create(
        package_nevra=package_nevra,
        repos=dumps(repos),
        defaults={
            'graph_json': dumps(graph_data)
        }
    )

    return new_nevra, new_graph