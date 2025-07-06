from celery import shared_task
from .models import Tracked_package
from .services.package_tracking import save_package_snapshot

@shared_task
def update_tracked_snapshots():
    tracked = Tracked_package.objects.all().order_by('repos')
    updated = 0

    for obj in tracked:
        name = obj.name
        repos = obj.get_repos()

        new_nevra, new_graph = save_package_snapshot(name, repos)
        
        if new_graph:
            updated += 1

    print(f"Обновили {updated} пакетов из {tracked.count()} отслеживаемых.")

    result = {'Обновленных пакетов': updated}
    
    return result
