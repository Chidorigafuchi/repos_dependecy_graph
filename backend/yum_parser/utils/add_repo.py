from typing import Dict
from yum_parser.models import Base_url, Repo_path


def add_repo_path(repo_url: str, repo_name: str) -> Dict[str, bool]:
        """
        Создаёт или получает объекты Base_url и Repo_path для
        заданного базового URL и имени репозитория.

        Args:
            repo_url (str): Адрес базового URL репозитория.
            repo_name (str): Название репозитория.

        Returns:
            Dict[str, bool]: Словарь с флагами создания новых записей:
                - 'base_url_created': был ли создан новый объект Base_url;
                - 'repo_path_created': был ли создан новый объект Repo_path.
        """
        repo_url_obj, new_base_url = Base_url.objects.get_or_create(base_url=repo_url)
        
        repo_path_obj, new_repo_path = Repo_path.objects.get_or_create(
            base_url=repo_url_obj,
            name=repo_name
        )
        
        return {'base_url_created': new_base_url, 'repo_path_created': new_repo_path}