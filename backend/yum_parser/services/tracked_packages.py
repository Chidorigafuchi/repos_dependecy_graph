from typing import Dict, List, Tuple
from django.db import DatabaseError
from collections import defaultdict
import logging

from ..models import Tracked_package
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def get_tracked_packages_list(session_key: str) -> Dict[Tuple[str], List[str]]:
    """
    Возвращает список отслеживаемых пользователем пакетов, сгруппированных по репозиториям.

    Фильтрует результат `get_tracked_packages()` по `session_key` и оставляет только пакеты,
    добавленные конкретным пользователем (идентифицируемым по сессии).

    Args:
        session_key (str): Ключ сессии пользователя для фильтрации пакетов.

    Returns:
        Dict[Tuple[str], List[str]]: Словарь, где ключ — список репозиториев, 
        а значение — список пакетов, отслеживаемых пользователем.
    """
    try:
        tracked = Tracked_package.objects.all()
    except DatabaseError as e:
        logger.error(f'Ошибка при получении отслеживаемых из БД: {e}')
        return {}

    packages_repos_for_user = defaultdict(list)
    
    for package in tracked:
        package_name = package.name
        if package.session_key == session_key:
            repo_paths = [tp_repo.repo for tp_repo in package.tracked_package_repo_set.all()]
            repos = [repo.get_full_url() for repo in repo_paths]
            packages_repos_for_user[package_name].append(repos)

    return packages_repos_for_user
