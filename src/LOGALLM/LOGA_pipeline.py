import os
import json
from time import sleep 
import streamlit as st 
from datasets import load_from_disk
import pandas as pd 
import numpy as np

import threading # 多线程
from concurrent.futures import ThreadPoolExecutor

from .Argument_Generator import Argument_Generator
from .streamlit_UI import UIManager
from .LLM_Manager import *

WORKERS = 8

class LOGA_pipeline:
    def __init__(self, mode, dataset, llm):
        self.mode = mode
        self.dataset = dataset
        self.llm = llm
        if self.dataset is not None:
            self._run_new_data()
        else:
            self._run_streamlit() 

    '''--------------------------<<Use Streamlit>>--------------------------'''
    def _run_streamlit(self, **kwargs):
        ui = UIManager()
        # llm = self.choose_llm()
        ui.run()
    '''--------------------------<<Utils>>--------------------------'''

    def _read_data(self):
        with open(os.path.join(self.dataset, 'data.json'), 'r') as f:
            data = json.loads(f.read())
        return data

    def save_json(self, data, path):
        try: 
            json.dumps(data)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'save in {path}')
        except TypeError as e:
            print(f"数据包含不可序列化的对象: {e} {path}")
        except Exception as e:
            print(f"保存JSON文件时出错: {e} {path}")

    '''--------------------------<<Use New Dataset>>--------------------------'''
    def _run_new_data(self, **kwarfs):

        data = self._read_data()
        
        files = os.listdir(self.dataset)
        print(files, len(files))
        stroage_path = os.path.join(self.dataset, f'res_{str(len(files))}')
        # ag = Argument_Generator(self.llm)
        os.makedirs(stroage_path)
        thread_local = threading.local()

        def process_item(i, idx):
            # return i
            if not hasattr(thread_local,"ag"):
                thread_local.ag = Argument_Generator(self.llm)
            ag = thread_local.ag
            this_id = i['id']
            print(f'start {this_id}')
            this_claim = i['claim']
            args = ag.get_arguments(this_claim)
            # print(args['claim'])
            json_path = f'{stroage_path}/{this_id}.json'
            self.save_json(args, json_path)
            print(f'fin {this_id}')
            # sleep()
            # pass

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            # ag = Argument_Generator(self.llm)
            futures = []
            for idx, i in enumerate(data):
                idx += 1 
                futures.append(executor.submit(
                    process_item, 
                    i,
                    idx
                ))
            for future in futures:
                future.result()
        





