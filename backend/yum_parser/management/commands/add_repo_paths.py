from django.core.management.base import BaseCommand
from backend.yum_parser.utils.add_repo import add_repo_path


class Command(BaseCommand):
    help = "Add base repositories of Red OS"

    def handle(self, *args, **kwargs):
        repos = ['os/', 'updates/', 'debuginfo/', 'kernel-rt/', 'kernel-testing/']
        
        for repo in repos:
            repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/'
            add_repo_path(repo_url, repo)
        

    