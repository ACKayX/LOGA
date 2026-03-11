import os
import re
import yaml 
import json 
import shutil
from .LLM_Manager import *

class Argument_Generator:
    def __init__(self, model):
        self._model = None
        self._llm = model
        self.claim = None

    def _get_llm(self):
        if self._llm == "deepseek":
            return DS_manager()
        else:
            return Sflow_manager()

    def save_file(self, name, content):
        with open(os.path.join(f"./data/ELSE/temp/{name}.txt"),'w') as f:
            f.write(content)
    
    def correct_yaml_format(self, content):
        content = content.replace('```yaml','').replace('```','').replace('。','.')
        content = content.replace('：',':')
        return content

    def generate_support_args(self, claim):
        prompt_choice = "support"
        output = self._llm.set_parameter(prompt_choice, claim, model=self._model)
        name = "support"
        self.save_file(name, output)
        output = self.correct_yaml_format(output)
        support_output = self._yaml_to_json(output)
        return support_output

    def _yaml_to_json(self, content):
        data = yaml.safe_load(content)
        return data

    def generate_attack_args(self, support, index, claim):
        prompt_choice = "attack"
        full_claim = {
            "claim": claim,
            "support_argument": support
        }
        output = self._llm.set_parameter(prompt_choice, full_claim, model=self._model)
        name = "attack"
        self.save_file(f"{name}_{index}", output)
        output = self.correct_yaml_format(output)
        attack_output = self._yaml_to_json(output)
        return attack_output


    def get_arguments(self, claim):
        # self.claim = claim
        if type(self._llm) == str:
            self._llm = self._get_llm()
        supports = self.generate_support_args(claim)
        this_data = {
            "claim": claim,
            "Args": {}
        }
        attacks = []

        # print(supports)
        for idx, support in enumerate(supports['Arguments']):
            # print(idx, support)
            attack = self.generate_attack_args(support, idx, claim)
            this_data['Args'][f'A{idx+1}'] = {
                "supporting": support,
                "attacks": attack['Arguments']
            }
        return this_data
