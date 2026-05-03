from rest_framework import generics
from news.models import NewsItem
from news.serializers import NewsItemSerializer

class NewsListView(generics.ListAPIView):
    serializer_class = NewsItemSerializer
    queryset = NewsItem.objects.select_related("source").order_by("-published_at")