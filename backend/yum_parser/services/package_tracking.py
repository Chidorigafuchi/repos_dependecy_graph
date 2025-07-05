from .graph import Graph
from .package_info import Package_info
from ..models import TrackedPackage, TrackedPackageSnapshot
from json import dumps


def track_package(session_key, package_name, repos):
    if package_name in Graph.packages.keys():
        obj, created = TrackedPackage.objects.get_or_create(
            session_key=session_key,
            name=package_name
        )
        
        if created:
            new = save_package_snapshot(package_name, repos)

        return {'track_created': created}

    return 

def save_package_snapshot(package_name, repos):
    info = Package_info.get_package_info(package_name)
    graph_data = Graph.get_package_graph(package_name, repos)

    snapshot, created = TrackedPackageSnapshot.objects.get_or_create(
        name=package_name,
        nevra=info['nevra'],
        defaults={
            'obsoletes': dumps(info['obsoletes']),
            'conflicts': dumps(info['conflicts']),
            'graph_json': dumps(graph_data),
        }
    )

    if created:
        print('Сохранили текущую версию для пакета - ', package_name)
        print(snapshot)
    else:
        print('Текущая версия пакета - ', package_name, ' уже была сохранен')

    return created
