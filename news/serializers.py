from rest_framework import serializers
from news.models import NewsItem

class NewsItemSerializer(serializers.ModelSerializer):
    source_name = serializers.ReadOnlyField(source="source.name")
    
    class Meta:
        model = NewsItem
        fields = ["id", "source_name", "title", "url", "summary", "published_at", "fetched_at"]