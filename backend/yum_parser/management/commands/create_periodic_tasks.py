from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = "Create or update periodic task to run update_tracked_snapshots every 10 minutes"

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        update_snapshots_command = 'yum_parser.tasks.update_tracked_snapshots'
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
        
    def create_periodic_task(self, schedule, task, task_name, message):
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