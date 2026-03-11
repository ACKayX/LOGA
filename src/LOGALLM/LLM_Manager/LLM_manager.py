import os
# import json

class LLM_manager:
    def __init__(self):
        pass

    def get_prompt(self):
        path = "./configs/prompts"
        prompt_files = [i for i in os.listdir(path) if i.endswith('txt')]
        prompts = {}
        for file in prompt_files:
            with open(os.path.join(path, file), 'r') as f:
                content = f.read()
            prompts[file.split('_')[0]] = content
        # print(prompts)
        return prompts


    def set_parameter(self,prompt_choice, text, **kwargs):
        raise NotImplementedError

    
    def _get_response(self, message):
        raise NotImplementedError

    