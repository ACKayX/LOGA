from .LLM_manager import LLM_manager
from google import genai


GM_API_KEY = "AIzaSyD7kssz6ryg4VOfPJIYzX_HRWpCXI6cM4Q"

class GM_manger(LLM_manager):
    def __init__(self):
        super().__init__()
        self.prompts = super().get_prompt()
        self.api_key = GM_API_KEY
        self.client = genai.Client()

    def set_parameter(self,prompt_choice, text, **kwargs):
        prompt = self.prompts[prompt_choice]

        model = "Gemma 3 27B"

        contents = ""
        message = [model, contents]

        return self._get_response()


    def _get_response(self, message):
        client = genai.Client()

        response = client.models.generate_content(
            *message
        )
        res = response.text
        res.replace('**','').replace('```','')
        return res


    # def get_condition_parameter(self):


