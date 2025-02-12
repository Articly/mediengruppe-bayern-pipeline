from typing import List

from bs4 import BeautifulSoup
import requests

from src.schemas import Article


def enrich_articles(selected_articles: List[Article]) -> List[Article]:
    enriched_articles = []
    for article in selected_articles:
        enriched_article = _enrich_article(article)
        enriched_articles.append(enriched_article)
    return enriched_articles


def _enrich_article(article: Article) -> Article:
    url = article.link
    article_text = _fetch_article_text(url)
    article.text = article_text
    return article


def _fetch_article_text(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        return ""
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = "\n\n".join([p.text for p in paragraphs])
    return text
