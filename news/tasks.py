import feedparser
from celery import shared_task
from dateutil.parser import parse as parse_date
from news.models import NewsSource, NewsItem
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_news():
    sources = NewsSource.objects.all()
    
    for source in sources:
        try:
            feed = feedparser.parse(source.feed_url)
            
            for entry in feed.entries:
                title = entry.get("title", "")
                url = entry.get("link", "")
                summary = entry.get("summary", "")
                published_str = entry.get("published", None)

                if not url:
                    continue

                try:
                    published_at = parse_date(published_str) if published_str else None
                except Exception:
                    published_at = None

                if published_at is None:
                    continue

                NewsItem.objects.get_or_create(
                    url=url,
                    defaults={
                        "source": source,
                        "title": title,
                        "summary": summary,
                        "published_at": published_at,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to fetch feed {source.feed_url}: {e}")
            continue