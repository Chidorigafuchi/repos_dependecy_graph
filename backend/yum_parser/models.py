from django.db import models
from django.contrib.auth.models import User

class TrackedPackage(models.Model):
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    tracked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_key', 'name')

    def __str__(self):
        return f"{self.session_key} tracks {self.name} - {self.version}"