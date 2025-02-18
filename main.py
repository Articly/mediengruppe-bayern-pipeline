import os

from src.ai_engine_connector import AIEngineConnector
from src.rss_consumer import RSSConsumer
from src.strapi_connector import StrapiConnector
# from src.utils import update_transcript_for_correct_pronounciations
# from src.article_selection import select_articles
from src.article_crawler import enrich_articles

DEFAULT_AUDIO_OPT_PROMPT_NAME = 'MGB-audio-optimization'
DEFAULT_PROMPT_NAME = 'MGB - Mediengruppe Bayern'


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
    articles = enrich_articles(articles)

    llm_input = "Begrüßung:\n" + intro_outro[0].get('intro') + "\n\n"
    for i, article in enumerate(articles):
        llm_input += f"Artikel {i+1}:\n{article.title}\n{article.summary}\n{article.text}\n\n"
    llm_input += "Verabschiedung:\n" + intro_outro[1].get('outro')

    transcript = ai_engine.chat_gpt_call(llm_input, prompt)
    print("First transcript")
    print(transcript)
    transcript = ai_engine.chat_gpt_call(transcript, audio_prompt)
    print("Second transcript")
    print(transcript)

    audio_product_id = strapi.create_audio_product()
    strapi.create_transcript(
        order=0, 
        llm_model=model_config["model"], 
        prompt=prompt, 
        llm_input=llm_input, 
        transcript=transcript, 
        audio_product_id=audio_product_id)


if __name__=="__main__":
    main()
