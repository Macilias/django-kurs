from django.db import models
from datetime import timedelta
from django.utils import timezone


class Poll(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    published_time = models.DateTimeField()
    days_running = models.IntegerField(default=7)

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def is_active(self):
        end_time = self.published_time + timedelta(days=self.days_running)
        return self.published_time <= timezone.now() <= end_time


class Choice(models.Model):
    poll = models.ForeignKey(to='Poll', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    votes = models.IntegerField(default=0)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.poll.name} ({self.name})"
