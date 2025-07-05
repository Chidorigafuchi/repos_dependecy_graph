from django.db import models

class TrackedPackage(models.Model):
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('session_key', 'name')

    def __str__(self):
        return f"{self.session_key} tracks {self.name}"