import os
import requests


class AIEngineConnector:
    """Class for interacting with AI Engine"""

    def __init__(self, model_config: dict) -> None:
        self.ai_engine_address = os.getenv("AI_ENGINE_ADDRESS").rstrip()
        self.llm_endpoint = '/llm'
        self.llm = "chatgpt-self-hosted" if model_config['self_hosted'] else "chatgpt"
        self.model = model_config['model']


    def chat_gpt_call(self, text: str, prompt: str, jsonify=False) -> str:
        llm_config = {
            'llm': self.llm,
            'model': self.model,
            "prompt": prompt,
            "input": text
        }
        if jsonify:
            llm_config['response_format'] = {"type": "json_object"}
        
        print('Doing OpenAI ChatGPT call...')
        response = requests.post(self.ai_engine_address + self.llm_endpoint, json=llm_config)

        if response.status_code == 200:
            json_response = response.json()
            result = json_response.get('result', 'No result found')
        else:
            raise Exception(f"Failed to get a successful response from the AI Engine for LLM call, status code: {response.status_code}")
        print('OpenAI ChatGPT call done!')
        return result
