import datetime
import json
import logging
import os

from src.ai_engine_connector import AIEngineConnector
from src.rss_consumer import RSSConsumer
from src.strapi_connector import StrapiConnector
# from src.utils import update_transcript_for_correct_pronounciations
# from src.article_selection import select_articles
from src.article_crawler import enrich_articles
from src.utils import get_date_with_german_month

DEFAULT_AUDIO_OPT_PROMPT_NAME = 'MGB-audio-optimization'
DEFAULT_PROMPT_NAME = 'MGB - Mediengruppe Bayern New'


def main():
    strapi = StrapiConnector()
    intro_outro = strapi.get_intro_and_outro()

    prompt = strapi.get_prompt(os.getenv("PROMPT_NAME", DEFAULT_PROMPT_NAME))
    audio_prompt = strapi.get_prompt(os.getenv("AUDIO_OPTIMIZATION_PROMPT_NAME", DEFAULT_AUDIO_OPT_PROMPT_NAME))

    model_config = strapi.get_model_config()

    ai_engine = AIEngineConnector(model_config)

    # tags = []
    rss = RSSConsumer()
    articles = rss.fetch_articles()
    # if it is monday get articles from the whole weekend, otherwise from the last day
    monday = False
    if datetime.datetime.today().weekday() == 0:
        monday = True
    
    if monday:
        articles = rss.filter_out_last_n_hours(articles, 48)
    else:
        articles = rss.filter_out_last_n_hours(articles, 24)
    
    if len(articles) == 0:
        raise Exception(f"No articles found from the last {'48' if monday else '24'} hours.")

    articles = enrich_articles(articles)

    intro, outro = intro_outro[0].get('intro'), intro_outro[1].get('outro')
    llm_input = ""
    for i, article in enumerate(articles):
        llm_input += f"Artikel {i+1}:\n{article.title}\n{article.summary}\n{article.text}\n\n"

    teaser_and_topics_string = ai_engine.chat_gpt_call(llm_input, prompt, jsonify=True)
    teaser_and_topics = json.loads(teaser_and_topics_string)
    teaser = teaser_and_topics.get('teaser')
    topics = teaser_and_topics.get('topics')
    # topic_1_short_title = f"{teaser_and_topics.get('topic_1_short_title')}  | Niederbayern-News vom {get_date_with_german_month()}"
    topic_1_short_title = f"{teaser_and_topics.get('topic_1_short_title')}  - Niederbayern-News vom {get_date_with_german_month()}"
    
    topics = [ai_engine.chat_gpt_call(topic, audio_prompt) for topic in topics]
    
    subtitle = "Tägliche Nachrichten aus deiner Region"

    audio_product_id = strapi.create_audio_product(
        title=topic_1_short_title,
        subtitle=subtitle, description=intro + "\n" + teaser,
        whatsapp_text_message=teaser + "\n🎵🎧 Dir gefällt dieser Audio-Service? Dann lass gerne einen Daumen da 👍"
    )
    
    strapi.create_transcript(
        order=0,
        transcript=intro + "\n"  + teaser,
        audio_product_id=audio_product_id
    )
    for i, topic in enumerate(topics):
        strapi.create_transcript(
            order=i + 1,
            transcript=topic,
            llm_model=model_config["model"], 
            prompt=prompt, 
            llm_input=llm_input, 
            audio_product_id=audio_product_id
        )
    strapi.create_transcript(
        order=i + 2,
        transcript=outro,
        audio_product_id=audio_product_id
    )


if __name__=="__main__":
    main()
