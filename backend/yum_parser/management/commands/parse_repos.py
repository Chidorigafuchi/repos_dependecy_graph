from django.core.management.base import BaseCommand
from yum_parser.services.parser import parse_repos 

class Command(BaseCommand):
    help = "Parses yum packages from the repositories"

    def handle(self, *args, **kwargs):
        parse_repos()