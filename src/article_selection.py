import random
from typing import List
from src.schemas import Article


def select_articles(articles: List[Article]):
    unselected_articles = _filter_out_republished(articles)
    unselected_articles = _filter_articles_from_today(unselected_articles)
    selected_articles = []

    while len(selected_articles) < 4 and len(unselected_articles) > 0:
        relevant_articles = _filter_articles_by_tag(unselected_articles, "Articly")
        if len(relevant_articles) > 0:
            relevant_articles = sorted(relevant_articles, key=lambda x: x.date, reverse=True)
            selected_articles.append(relevant_articles[0])
            unselected_articles = _remove_article_by_title(unselected_articles, relevant_articles[0].title)
        else:
            break

    segments = ["Politik", "Wirtschaft", "Panorama"]
    if len(selected_articles) == 1:
        segments = ["Politik", "Panorama", "Wirtschaft"]
    if len(selected_articles) == 2:
        segments = ["Panorama", "Politik", "Wirtschaft"]

    i = 0
    n = len(unselected_articles)
    while len(selected_articles) < 4 and len(unselected_articles) > 0:
        segment = segments[i % len(segments)]
        i += 1
        relevant_articles = _filter_articles_by_tag(unselected_articles, segment)
        if len(relevant_articles) > 0:
            relevant_articles = sorted(relevant_articles, key=lambda x: x.date, reverse=True)
            selected_articles.append(relevant_articles[0])
            unselected_articles = _remove_article_by_title(unselected_articles, relevant_articles[0].title)
        if i > n:
            break
    random.shuffle(selected_articles)
    return selected_articles


def _filter_out_republished(articles: List[Article]) -> List[Article]:
    return [article for article in articles if "Republished" not in article.tags]


def _filter_articles_from_today(articles: List[Article]) -> List[Article]:
    return [article for article in articles if article.date.date() == article.date.today().date()]


def _filter_articles_by_tag(articles: List[Article], tag: str) -> List[Article]:
    return [article for article in articles if tag in article.tags]


def _remove_article_by_title(articles: List[Article], title: str) -> List[Article]:
    return [article for article in articles if article.title != title]
