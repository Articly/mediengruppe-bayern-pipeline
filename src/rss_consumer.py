from datetime import datetime
import os
from typing import List, Dict

from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
import requests
import feedparser

from src.schemas import Article

germany_tz = ZoneInfo("Europe/Berlin")


class RSSConsumer:
    """Class for consuming RSS feeds."""

    def __init__(self) -> None:

        self.rss_feed = os.getenv("RSS_FEED","https://www.pnp.de/feeds/articly/niederbayern_podcast.xml")
        self.rss_feed_token = os.getenv("RSS_FEED_TOKEN").rstrip()

    def fetch_articles(self) -> List[Article]:
        rss_string = self._fetch_rss_feed()
        filtered_items = self._filter_items(rss_string)
        articles = self._parse_articles(filtered_items)
        return articles

    def _fetch_rss_feed(self) -> str:
        headers = {'Authorization': f'Bearer {self.rss_feed_token}'}

        try:
            print("Fetching RSS feed from %s", self.rss_feed)
            response = requests.get(self.rss_feed, headers=headers)

            response.raise_for_status()

            print("Successfully fetched RSS feed.")
            return response.text

        except requests.HTTPError as http_err:
            print("HTTP error occurred: %s", http_err)
            raise Exception(f"Failed to fetch RSS feed due to an HTTP error: {http_err}")

        except requests.RequestException as req_err:
            print("Request exception occurred: %s", req_err)
            raise Exception(f"Failed to fetch RSS feed due to a request error: {req_err}")

        except Exception as e:
            print("An unexpected error occurred: %s", e)
            raise Exception(f"An unexpected error occurred while fetching the RSS feed: {e}")

    def _filter_items(self, rss_string: str):
        feed = feedparser.parse(rss_string)

        filtered_items = []
        for item in feed.entries:
            filtered_items.append(item)
        return filtered_items

    def _parse_articles(self, items: List[Dict]) -> List[Article]:
        articles = []
        for item in items:
            try:
                date = parsedate_to_datetime(item.published)
                title = item.title
                summary = item.summary
                link = item.get('link', '')
                article = Article(date=date, title=title, link=link, summary=summary)
                articles.append(article)

            except Exception as e:
                print(f"Failed to parse article: {e}")
        return articles
    
    
    def filter_out_last_n_hours(self, articles: List[Article], n_hours: int) -> List[Article]:
        return [article for article in articles if (datetime.now(germany_tz) - article.date).total_seconds() / 3600 < n_hours]
