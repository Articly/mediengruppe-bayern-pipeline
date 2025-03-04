import os
import requests


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
            INTRO_OUTRO = os.environ.get('INTRO_OUTRO', 'MG-Bayern')
            for intro_data in res_data:
                if intro_data['attributes'].get('name') == INTRO_OUTRO:
                    intro_and_outro.append({'intro': intro_data.get('attributes').get('intro')})
                    intro_and_outro.append({'outro': intro_data.get('attributes').get('outro')})

        else:
            raise Exception(f"Failed to fetch intro_and_outro.\nStatus Code: {response.status_code}.\nError: {response.text}")

        return intro_and_outro


    def get_model_config(self) -> dict:
        # url = f"{self.api_url}mgb-audio-config?populate=chatgpt"
        url = f"{self.api_url}pro7-audio-config?populate=chatgpt"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            config = response.json()
            chatgpt_config = config.get('data', {}).get('attributes', {}).get('chatgpt', {})
            self_hosted = chatgpt_config.get('self_hosted')
            model = chatgpt_config.get('model')
            return {'self_hosted': self_hosted, 'model': model}
        else:
            raise Exception(
                f"Failed to retrieve audio config from Strapi.\n"
                f"Status Code: {response.status_code}.\n"
                f"Error: {response.text}"
            )

    def create_audio_product(self) -> int:
        url = f"{self.api_url}mgb-audio-products"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.strapi_api_key}'
        }
        data = {"data": {}}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            created_entry = response.json()
            entry_id = created_entry.get('data', {}).get('id')
            print(f"Entry created with ID: {entry_id}")
        else:
            raise Exception(f"Failed to create entry in Strapi.\nStatus Code: {response.status_code}.\nError: {response.text}")
        return entry_id

    def create_transcript(self, order, llm_model, prompt, llm_input, transcript, audio_product_id) -> None:
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
