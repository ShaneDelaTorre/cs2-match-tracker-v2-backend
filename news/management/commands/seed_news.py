from django.core.management.base import BaseCommand
from news.models import NewsSource

class Command(BaseCommand):
    help = "Seed news sources"

    def handle(self, *args, **options):
        sources = [
            {
                "name": "CS2 Official News",
                "feed_url": "https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-en.xml",
            },
            {
                "name": "CS2 Official Updates",
                "feed_url": "https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-en.xml",
            },
            {
                "name": "Dust2.us",
                "feed_url": "https://www.dust2.us/feed/",
            },
        ]

        for source in sources:
            obj, created = NewsSource.objects.get_or_create(
                feed_url=source["feed_url"],
                defaults={"name": source["name"]},
            )
            if created:
                self.stdout.write(f"  Created: {source['name']}")
            else:
                self.stdout.write(f"  Already exists: {source['name']}")

        self.stdout.write(self.style.SUCCESS("News sources seeded."))