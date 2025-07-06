from django.db import models
import json

class Tracked_package(models.Model):
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    repos = models.TextField(default='[]')

    class Meta:
        unique_together = ('session_key', 'name', 'repos')

    def get_repos(self):
        return json.loads(self.repos)

    def __str__(self):
        return f"{self.session_key} tracks {self.name}"


class Package_nevra(models.Model):
    name = models.CharField(max_length=255)
    nevra = models.CharField(max_length=255)
    obsoletes = models.TextField(null=True, blank=True)
    conflicts = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'nevra')

    def get_obsoletes(self):
        return json.loads(self.obsoletes or "[]")

    def get_conflicts(self):
        return json.loads(self.conflicts or "[]")

    def __str__(self):
        return f"{self.name} [{self.nevra}]"


class Package_repos_graph(models.Model):
    package_nevra = models.ForeignKey(Package_nevra, on_delete=models.CASCADE)
    repos = models.TextField(default='[]')
    graph_json = models.TextField(default='{}')

    class Meta:
        unique_together = ('package_nevra', 'repos')

    def get_repos(self):
        return json.loads(self.repos)

    def get_graph(self):
        return json.loads(self.graph_json or "{}")

    def __str__(self):
        return f"{self.package_nevra} [{self.repos}] Graph"