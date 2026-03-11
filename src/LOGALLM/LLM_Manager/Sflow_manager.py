import os
import requests

from .LLM_manager import LLM_manager


class Sflow_manager(LLM_manager):
    def __init__(self):
        super().__init__()
        self.prompts = super().get_prompt()
        self.api_key = 'sk-bwoagxuqyasxezxxnpbskbculhwrmlnvigsbxffyvwdfnjbz'
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
    
    def set_parameter(self, prompt_choice, text, **kwargs):
        model = kwargs.get('model')
        prompt = self.prompts[prompt_choice]
        message = {
            "model": f'{model}', # 模型选择
            "messages": [
                {
                    "role": "system",
                    "content": f"{prompt}" # LLM 系统设定
                },
                {
                    "role": "user",
                    "content": f"{text}" # 处理内容
                }
            ],
            "stream": False,
            "temperature": 0.5,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1
        }
        return self._get_response(message)
    
    def _get_response(self, message):
        payload = message

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()

        res = response_data['choices'][0]['message']['content']
        return res