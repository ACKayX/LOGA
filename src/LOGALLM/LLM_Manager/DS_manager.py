from .LLM_manager import LLM_manager
from openai import OpenAI

class DS_manager(LLM_manager):
    def __init__(self):
        super().__init__()
        self.prompts = super().get_prompt()
        self.api_key = "sk-c7e3c5092aa444919ae33634fab645b8"
    
    def set_parameter(self, prompt_choice, text, **kwargs):
        prompt = self.prompts[prompt_choice]

        message = [
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{text}"},
        ]
        # print(message)
        # return message
        return self._get_response(message)

    def _get_response(self, message):
        client = OpenAI(api_key=f"{self.api_key}", base_url="https://api.deepseek.com")

        # print(message)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=message,
                stream=False
        )
        # print(message)
        res = response.choices[0].message.content
        res.replace('**','').replace('```','')
        # print(res)
        return res


    def get_condtion_parameter(self, prompt, claim, argus):
        message = [
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{claim},Argument: {argus}"},
        ]
        # print(message)
        return self._get_response(message)
