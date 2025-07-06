import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repos_dependency_graph.settings')

app = Celery('repos_dependency_graph')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
