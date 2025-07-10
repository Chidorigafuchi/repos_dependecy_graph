from django.db import models
import json


class Base_url(models.Model):
    base_url = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"url for repos - {self.base_url}"


class Repo_path(models.Model):
    base_url = models.ForeignKey(Base_url, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def get_full_url(self) -> str:
            base = self.base_url.base_url.rstrip('/')
            repo = self.name.strip('/')
            return f"{base}/{repo}/"

    def __str__(self):
        return f"repo - {self.name} from - {self.base_url}"


class Tracked_package(models.Model):
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    repos_hash = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.session_key} tracks {self.name}"
    

class Tracked_package_repo(models.Model):
    tracked_package = models.ForeignKey(Tracked_package, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repo_path, on_delete=models.CASCADE)


class Package_nevra_info(models.Model):
    tracked_package = models.OneToOneField('Tracked_package', on_delete=models.CASCADE, related_name='package_info')
    nevra = models.CharField(max_length=255)
    obsoletes = models.TextField(null=True, blank=True)
    conflicts = models.TextField(null=True, blank=True)
    graph_json = models.TextField(default='{}')

    def get_obsoletes(self):
        return json.loads(self.obsoletes or "[]")

    def get_conflicts(self):
        return json.loads(self.conflicts or "[]")

    def get_graph(self):
        return json.loads(self.graph_json or "{}")

    def __str__(self):
        return f"Info for tracked package: {self.tracked_package.name}"

    @property
    def repos(self):
        return [link.repo for link in self.tracked_package.package_repos.all()]