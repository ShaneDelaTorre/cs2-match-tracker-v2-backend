import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from news.models import NewsSource, NewsItem
from news.tasks import fetch_news


@pytest.fixture
def news_source():
    return NewsSource.objects.create(
        name="Test Source",
        feed_url="https://example.com/feed.xml",
    )


def make_mock_feed(entries):
    feed = MagicMock()
    feed.entries = entries
    return feed


def make_entry(title, link, summary, published):
    entry = MagicMock()
    entry.get = lambda key, default="": {
        "title": title,
        "link": link,
        "summary": summary,
        "published": published,
    }.get(key, default)
    return entry


@pytest.mark.django_db
class TestFetchNews:
    def test_creates_news_items_from_feed(self, news_source):
        entry = make_entry(
            title="CS2 Update",
            link="https://example.com/article/1",
            summary="A new update dropped.",
            published="Tue, 29 Apr 2026 10:00:00 GMT",
        )
        mock_feed = make_mock_feed([entry])

        with patch("news.tasks.feedparser.parse", return_value=mock_feed):
            fetch_news()

        assert NewsItem.objects.count() == 1
        item = NewsItem.objects.first()
        assert item.title == "CS2 Update"
        assert item.source == news_source

    def test_idempotent_does_not_duplicate(self, news_source):
        entry = make_entry(
            title="CS2 Update",
            link="https://example.com/article/1",
            summary="A new update dropped.",
            published="Tue, 29 Apr 2026 10:00:00 GMT",
        )
        mock_feed = make_mock_feed([entry])

        with patch("news.tasks.feedparser.parse", return_value=mock_feed):
            fetch_news()
            fetch_news()

        assert NewsItem.objects.count() == 1

    def test_skips_entry_without_url(self, news_source):
        entry = make_entry(
            title="No URL Article",
            link="",
            summary="Missing link.",
            published="Tue, 29 Apr 2026 10:00:00 GMT",
        )
        mock_feed = make_mock_feed([entry])

        with patch("news.tasks.feedparser.parse", return_value=mock_feed):
            fetch_news()

        assert NewsItem.objects.count() == 0

    def test_skips_entry_without_published_date(self, news_source):
        entry = make_entry(
            title="No Date Article",
            link="https://example.com/article/2",
            summary="Missing date.",
            published=None,
        )
        mock_feed = make_mock_feed([entry])

        with patch("news.tasks.feedparser.parse", return_value=mock_feed):
            fetch_news()

        assert NewsItem.objects.count() == 0

    def test_continues_if_one_source_fails(self):
        NewsSource.objects.create(
            name="Bad Source",
            feed_url="https://bad-source.com/feed.xml",
        )
        good_source = NewsSource.objects.create(
            name="Good Source",
            feed_url="https://good-source.com/feed.xml",
        )
        entry = make_entry(
            title="Good Article",
            link="https://good-source.com/article/1",
            summary="Works fine.",
            published="Tue, 29 Apr 2026 10:00:00 GMT",
        )

        def mock_parse(url):
            if "bad" in url:
                raise Exception("Feed unavailable")
            return make_mock_feed([entry])

        with patch("news.tasks.feedparser.parse", side_effect=mock_parse):
            fetch_news()

        assert NewsItem.objects.count() == 1