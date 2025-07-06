from .graph import Graph
from .package_info import Package_info
from ..models import TrackedPackage, TrackedPackageSnapshot
from json import dumps
from typing import Dict, List, Optional


def track_package(
        session_key: str, 
        package_name: str, 
        repos: List[str]
) -> Optional[Dict[str, bool]]:
    if package_name in Graph.packages.keys():
        obj, created = TrackedPackage.objects.get_or_create(
            session_key=session_key,
            name=package_name,
            repos=dumps(repos)
        )
        
        if created:
            new = save_package_snapshot(package_name, repos)

        return {'track_created': created}

    return 

def save_package_snapshot(package_name: str, repos: List[str]) -> bool:
    info = Package_info.get_package_info(package_name)
    graph_data = Graph.get_package_graph(package_name, repos)

    snapshot, created = TrackedPackageSnapshot.objects.get_or_create(
        name=package_name,
        nevra=info['nevra'],
        repos=dumps(repos),
        defaults={
            'obsoletes': dumps(info['obsoletes']),
            'conflicts': dumps(info['conflicts']),
            'graph_json': dumps(graph_data),
        }
    )

    return created
