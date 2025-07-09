from typing import List
import logging
from django_celery_beat.models import IntervalSchedule

from .create_periodic_tasks import create_periodic_task, disable_periodic_task
from repos_dependency_graph.services.redis import redis_expire_extend

logger = logging.getLogger(__name__)

TASK_NAME = 'periodic_parse_repos_retry'
COMMAND = 'yum_parser.tasks.parse_repos_task'
PERIOD_MINUTES = 10


def reparse_repos(unloaded_repos: List[str] = None) -> None:
    """
    Создаёт или обновляет периодическую задачу для парсинга репозиториев в случае неполного парсинга
    
    Args
        unloaded_repos (List[str]): Список незагруженных репозиториев для дозагрузки
    
    Returns:
        None
    """
    if unloaded_repos is None:
        unloaded_repos = []
        redis_expire_extend('repos_dependencies:compressed', 60 * 5)
        redis_expire_extend('repos_info:compressed', 60 * 5)
        logger.info("Продлён TTL кэша repos_dependencies и repos_info на 5 минут")

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=PERIOD_MINUTES,
        period=IntervalSchedule.MINUTES
    )

    create_periodic_task(
            TASK_NAME,
            schedule,
            COMMAND,
            'retry parse_repos',
            kwargs={'unloaded_repos': unloaded_repos}
        )
    
def disable_reparse_repos() -> None:
    disable_periodic_task(TASK_NAME)