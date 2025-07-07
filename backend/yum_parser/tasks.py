from celery import shared_task
import subprocess
from pickle import loads
from zlib import decompress
from collections import defaultdict

from .models import Tracked_package
from .services.graph import get_package_graph
from .services.package_tracking import save_package_snapshot
from .services.parser import repos_union
from repos_dependency_graph.services.redis import redis_cache


@shared_task
def update_tracked_snapshots():
    tracked = Tracked_package.objects.all().order_by('repos')
    updated = 0
    repos_packages = defaultdict(list)

    decompressed_data = decompress(redis_cache.get('repos_info:compressed'))
    packages_info = loads(decompressed_data)

    for package in tracked:
        repos = tuple(package.get_repos())
        repos_packages[repos].append(package)

    for repos_list in repos_packages.keys():
        group_repos_packages = repos_union(repos_list)

        for package in repos_packages[repos_list]:
            package_name = package.name

            graph = get_package_graph(package_name, repos_list, repos_packages=group_repos_packages)
            info = packages_info.get(package_name)

            new_nevra, new_graph = save_package_snapshot(package_name, repos_list, graph, info)
    
        if new_nevra:
            print(f'Обновил пакет - {package_name}')
            updated += 1

    print(f"Обновили {updated} пакетов из {tracked.count()} отслеживаемых.")

    result = {'Обновленных пакетов': updated}
    
    return result

@shared_task
def run_parse_packages_command():
    subprocess.run(["python", "manage.py", "parse_packages"], check=True)