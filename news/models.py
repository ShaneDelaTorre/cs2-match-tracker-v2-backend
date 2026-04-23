from django.db import models

# Create your models here.
class NewsSource(models.Model):
    name = models.CharField(max_length=128)
    feed_url = models.URLField(unique=True)

class NewsItem(models.Model):
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name="item")
    title = models.CharField(max_length=256)
    url = models.URLField(unique=True)
    summary = models.TextField(blank=True, default="")
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)