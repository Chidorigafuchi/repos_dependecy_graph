import json
from typing import Dict, List, Optional

from .graph import get_package_graph
from .package_info import get_package_info
from ..models import Tracked_package, Package_nevra, Package_repos_graph


def track_package(session_key: str, package_name: str, repos: List[str]) -> Optional[Dict[str, bool]]:
    created = False
    new_nevra = False
    
    repos.sort()
    
    obj, created = Tracked_package.objects.get_or_create(
        session_key=session_key,
        name=package_name,
        repos=json.dumps(repos)
    )
    
    if created:
        graph = get_package_graph(package_name, repos)
        info = get_package_info(package_name)
        new_nevra, new_graph = save_package_snapshot(package_name, repos, graph, info)

    return {'track_created': created, 'version_created': new_nevra}


def save_package_snapshot(package_name: str, repos: List[str], graph, info) -> bool:
    new_graph = False

    package_nevra, new_nevra = Package_nevra.objects.get_or_create(
        name=package_name,
        nevra=info['nevra'],
        defaults={
            'obsoletes': json.dumps(info['obsoletes']),
            'conflicts': json.dumps(info['conflicts']),
        }
    )

    if new_nevra:
        package_graph, new_graph = Package_repos_graph.objects.get_or_create(
            package_nevra=package_nevra,
            repos=json.dumps(repos),
            defaults={
                'graph_json': json.dumps(graph)
            }
        )

    return new_nevra, new_graph