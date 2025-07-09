import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import logging

logger = logging.getLogger(__name__)

def create_periodic_task(
    task_name: str,
    schedule: IntervalSchedule, 
    task: str,
    message: str,
    kwargs: dict = None
) -> None:
    """
    Создаёт или обновляет периодическую Celery-задачу через django-celery-beat.

    Args:
        task_name (str): название задачи
        schedule (IntervalSchedule): интервал работы задачи
        task (str): задача из tasks.py, которую нужно выполнять
        message (str) 
        kwargs (dict): именованные аргументы, которые будут переданы в задачу
    
    Returns:
        None
    """
    kwargs_json = json.dumps(kwargs or {})

    periodic_task, created = PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            'interval': schedule,
            'task': task,
            'kwargs': kwargs_json,
            'enabled': True,
        }
    )

    if created:
        logger.info(f'Periodic task {task_name} for {message} created.')
    else:
        logger.info(f'Periodic task {task_name} for {message} updated.')

def disable_periodic_task(
    task_name:str 
) -> None:
    """
    Отключают периодическую Celery-задачу через django-celery-beat по названию.
    
    Args:
        task_name (str): название задачи

    Returns:
        None
    """
    try:
        task = PeriodicTask.objects.get(name=task_name)
        task.enabled = False
        task.save()
        logger.info(f'Periodic task {task_name} disabled.')
    except PeriodicTask.DoesNotExist:
        logger.info(f'Periodic task {task_name} doesn\'t exist.')