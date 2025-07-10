from typing import Dict, List, Tuple
from django.db import DatabaseError
from collections import defaultdict
from hashlib import sha1
from json import dumps
import logging

from ..models import Tracked_package
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def get_tracked_packages_list(session_key: str) -> Dict[Tuple[str], List[str]]:
    """
    Возвращает список отслеживаемых пользователем пакетов, сгруппированных по репозиториям.

    Args:
        session_key (str): Ключ сессии пользователя для фильтрации пакетов.

    Returns:
        Dict[str, List[List[str]]]: Словарь, где ключ — название пакета, 
        а значение — список списков репозиториев, по которым отслеживается пакет пользователем.
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


def delete_tracked_package_from_db(session_key: str, package: str, repos: List[str]) -> bool:
    """
    Удаляет отслеживаемый пакет пользователя по имени, сессии и хэшу репозиториев.

    Args:
        session_key (str): Ключ сессии пользователя.
        package (str): Имя удаляемого пакета.
        repos (List[str]): Список URL-ов репозиториев, для которых удаляется отслеживание.

    Returns:
        bool: True, если удаление прошло успешно, False — в противном случае.
    """
    try:
        sorted_repos = sorted(repos)
        repos_hash = sha1(dumps(sorted_repos).encode()).hexdigest()
        
        tracked_package = Tracked_package.objects.get(
            session_key=session_key,
            name=package,
            repos_hash=repos_hash
        )

        tracked_package.delete()
        return True
    except DatabaseError as e:
        logger.error(f'Ошибка при удалении отслеживаемого пакета из БД: {e}')

    return False