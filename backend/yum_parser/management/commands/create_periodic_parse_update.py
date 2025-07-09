from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule
from backend.yum_parser.utils.create_periodic_tasks import create_periodic_task

class Command(BaseCommand):
    help = "Создает или обновляет переодические задачи на поиск новых версий пакетов, парсинг пакетов из репозиториев"

    def handle(self, *args, **kwargs) -> None:
        """
        Создаёт или обновляет две периодические задачи:
        - Поиск новых версий отслеживаемых пакетов
        - парсинг пакетов из репозиториев

        Returns
            None
        """
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        update_snapshots_command = 'yum_parser.tasks.update_tracked_packages'
        parse_packages_command = 'yum_parser.tasks.run_parse_packages_command'

        create_periodic_task(
            'Update snapshots of the tracked packages every 24 hours',
            schedule,
            update_snapshots_command,
            'tracking package\'s versions'
        )

        create_periodic_task(
            'Parse packages from repositories every 24 hours',
            schedule,
            parse_packages_command,
            'parsing packages from repositories'
        )