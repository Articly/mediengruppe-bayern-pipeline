import json
import os

from src.ai_engine_connector import AIEngineConnector
from src.rss_consumer import RSSConsumer
from src.strapi_connector import StrapiConnector
# from src.utils import update_transcript_for_correct_pronounciations
# from src.article_selection import select_articles
from src.article_crawler import enrich_articles

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

    # @TODO: Check if required
    # articles = select_articles(articles)
    # TODO: filter out articles using tag
    articles = enrich_articles(articles)

    intro, outro = intro_outro[0].get('intro'), intro_outro[1].get('outro')
    llm_input = ""
    for i, article in enumerate(articles):
        llm_input += f"Artikel {i+1}:\n{article.title}\n{article.summary}\n{article.text}\n\n"

    teaser_and_topics_string = ai_engine.chat_gpt_call(llm_input, prompt, jsonify=True)
    teaser_and_topics = json.loads(teaser_and_topics_string)
    teaser = teaser_and_topics.get('teaser')
    topics = teaser_and_topics.get('topics')
    
    topics = [ai_engine.chat_gpt_call(topic, audio_prompt) for topic in topics]

    audio_product_id = strapi.create_audio_product()
    
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
