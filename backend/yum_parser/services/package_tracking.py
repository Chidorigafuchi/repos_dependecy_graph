from .graph import Graph
from ..models import TrackedPackage


def track_package(session_key, package_name):
    if package_name in Graph.packages.keys():
        obj, created = TrackedPackage.objects.get_or_create(
            session_key=session_key,
            name=package_name
        )

        if not created:
            print(obj)
        return {'created': created}

    return 

