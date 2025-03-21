import os
import requests
from src.schemas import create_instance_from_dynamic_zone
from src.utils import get_date_with_german_month_without_year


class StrapiConnector:
    """Class for interacting with Strapi"""

    def __init__(self) -> None:
        strapi_external_domain = os.environ.get("STRAPI_EXTERNAL_DOMAIN").rstrip()
        self.api_url = f"{strapi_external_domain}api/"
        self.strapi_api_key = os.environ.get("STRAPI_API_KEY").rstrip()

    def get_prompt(self, prompt_name: str) -> str:
        url = f"{self.api_url}prompts?populate=*&filters[name][$eq]={prompt_name}"

        payload = {}
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.strapi_api_key}'
        }

        response = requests.get(url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to get a successful response from the Strapi API when trying to get a prompt, status code: {response.status_code}, response: {response.text}")

        if len(response.json()['data']) == 0:
            raise Exception(
                f"Failed to get a prompt with name {prompt_name} from the Strapi API, response: {response.text}")

        prompt = response.json()['data'][0]['attributes']['prompt']
        return prompt
    
    def format_intro(self, intro_text: str) -> str:
        return intro_text.replace('<date_format>', get_date_with_german_month_without_year())

    def get_intro_and_outro(self) -> str:
        intro_and_outro = []
        url = f"{self.api_url}intro-and-outros"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            res_data = response.json()['data']
            INTRO_OUTRO = os.environ.get('INTRO_OUTRO', 'MG-Bayern-v2')
            for intro_data in res_data:
                if intro_data['attributes'].get('name') == INTRO_OUTRO:
                    intro = self.format_intro(intro_data.get('attributes').get('intro'))
                    intro_and_outro.append({'intro': intro})
                    intro_and_outro.append({'outro': intro_data.get('attributes').get('outro')})

        else:
            raise Exception(f"Failed to fetch intro_and_outro.\nStatus Code: {response.status_code}.\nError: {response.text}")

        return intro_and_outro


    def get_model_config(self) -> dict:
        url = f"{self.api_url}mgb-audio-config?populate=llm"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            config = response.json()["data"]["attributes"]
            chatgpt_config_json = config.get('llm')[0]
            chatgpt_config = create_instance_from_dynamic_zone(chatgpt_config_json)
            
            self_hosted = chatgpt_config.self_hosted
            model = chatgpt_config.model
            return {'self_hosted': self_hosted, 'model': model}
        else:
            raise Exception(
                f"Failed to retrieve audio config from Strapi.\n"
                f"Status Code: {response.status_code}.\n"
                f"Error: {response.text}"
            )

    def create_audio_product(self, title, subtitle, description, whatsapp_text_message) -> int:
        url = f"{self.api_url}mgb-audio-products"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        data = {"data": {
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "whatsapp_text_message": whatsapp_text_message
        }}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            created_entry = response.json()
            entry_id = created_entry.get('data', {}).get('id')
            print(f"Entry created with ID: {entry_id}")
        else:
            raise Exception(f"Failed to create entry in Strapi.\nStatus Code: {response.status_code}.\nError: {response.text}")
        return entry_id

    def create_transcript(self, order, transcript, audio_product_id, llm_model=None, prompt=None, llm_input=None) -> None:
        url = f"{self.api_url}mgb-transcripts"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        data = {
            "data": {
                "type": "transcript",
                "order": order,
                "llm_model": llm_model,
                "prompt": prompt,
                "input": llm_input,
                "transcript": transcript,
                "audio_product_id": audio_product_id
            }
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code in [200, 201]:
            created_entry = response.json()
            entry_id = created_entry.get('data', {}).get('id')
            print(f"Entry created with ID: {entry_id}")
        else:
            raise Exception(
                f"Failed to create entry in Strapi.\n"
                f"Status Code: {response.status_code}.\n"
                f"Error: {response.text}"
            )