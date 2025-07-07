from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = "Create or update periodic task to run update_tracked_packages every 10 minutes"

    def handle(self, *args, **kwargs) -> None:
        """
        Создаёт или обновляет две периодические задачи:
        - обновление снимков отслеживаемых пакетов
        - парсинг пакетов из репозиториев
        """
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        update_snapshots_command = 'yum_parser.tasks.update_tracked_packages'
        parse_packages_command = 'yum_parser.tasks.run_parse_packages_command'

        self.create_periodic_task(
            schedule,
            update_snapshots_command,
            'Update snapshots of the tracked packages every 24 hours',
            'tracking package\'s versions'
        )

        self.create_periodic_task(
            schedule,
            parse_packages_command,
            'Parse packages from repositories every 24 hours',
            'parsing packages from repositories'
        )
        
    def create_periodic_task(
            self, 
            schedule: IntervalSchedule, 
            task: str, 
            task_name: str, 
            message: str
        ) -> None:
        """
        Создаёт или обновляет периодическую задачу Celery Beat.

        Args:
            schedule (IntervalSchedule): Интервал выполнения задачи.
            task (str): Имя задачи для Celery (полное имя функции).
            task_name (str): Уникальное имя задачи в базе PeriodicTask.
            message (str): Сообщение для чего используется задача в stdout после создания/обновления.
        """
        periodic_task, created = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                'interval': schedule,
                'task': task,
                'enabled': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Periodic task for {message} created.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Periodic task for {message} updated.'))