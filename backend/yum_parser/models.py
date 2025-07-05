from django.db import models
import json

class TrackedPackage(models.Model):
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('session_key', 'name')

    def __str__(self):
        return f"{self.session_key} tracks {self.name}"


class TrackedPackageSnapshot(models.Model):
    name = models.CharField(max_length=255)
    nevra = models.CharField(max_length=255, unique=True)
    obsoletes = models.TextField(null=True, blank=True)
    conflicts = models.TextField(null=True, blank=True)
    graph_json = models.TextField()

    class Meta:
        unique_together = ('name', 'nevra')

    def get_obsoletes(self):
        return json.loads(self.obsoletes or "[]")

    def get_conflicts(self):
        return json.loads(self.conflicts or "[]")

    def get_graph(self):
        return json.loads(self.graph_json or "{}")

    def __str__(self):
        return f"{self.name} [{self.nevra}]"
    
    