import streamlit as st
from abc import ABC, abstractmethod
import json
import os
import pandas as pd 

from ..ARTree import *

class Base_page(ABC):
    def __init__(self, name):
        st.header(f'{name}')

    @abstractmethod
    def run(self, llm, update):
        raise NotImplementError

    def create_table_row(self, data, res, edges, nodes):
        """创建表格行数据"""
        return {
            'ID': data['id'],
            'LABEL': data['label'],
            'CLs': res,
            'args': [edges, nodes, data['claim']],
        }

    def read_data(self, path):
        try:
            with open(path, 'r') as f:
                data = json.loads(f.read())
            return data
        except Exception as e:
            print(path)
            raise Exception

    def step_tree_const(self, data, **kwargs):
        rt = ART_Reasoner()
        art = ART_Tree()
        art.get_data(data)
        infos = art.update(kwargs['update'])
        infos['this_path'] = kwargs['this_path']
        infos['llm'] = kwargs['llm']
        infos['id'] = kwargs['id']
        rt.begin(infos)
        result = rt.reasoning()
        return infos, result

    def save_json(self, data,path):
        try:
            json.dumps(data)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'save in {path}')
        except TypeError as e:
            print(f"数据包含不可序列化的对象: {e} {path}")
        except Exception as e:
            print(f"保存JSON文件时出错: {e} {path}")

    def get_list_dataset(self):
        data_path = "./data"
        data_list = {i: os.path.join(data_path,i) for i in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,i)) and i != 'ELSE'}
        # st.markdown(data_list)
        names = list(data_list.keys())
        st.sidebar.header('Set Dataset')
        dataset = st.sidebar.radio(
            'select dataset to evaluate',
            options=names
        )
        return data_list[dataset]

    def set_update(self, idx=None):
        update_option = [
            'tanh(nb_CA - nb_CR)',
            '- MAX (CA - CR)',
            'MAX(CA) - MAX(CR)',
            'tanh(SUM(CA)-SUM(CR))',
            'split(nb_CA/nb_C)',
            '-1',
            'ATTACK_relation'
        ]
        if idx is None:
            st.sidebar.header('Set Update choice')
            update = st.sidebar.radio(
                'select how to update score',
                options=update_option,
                index=2
            )
        else: update = update_option[idx]
        the_index = update_option.index(update)
        return the_index
    '''设置权重更新方法'''

    def read_full_dataset(self, path):
        folder_l = [int(f.split('_')[-1]) for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]
        # st.markdown(f'{path} - {folder_l}')
        the_num = max(folder_l)
        folder = os.path.join(path, f'res_{the_num}')
        # st.markdown(f'Reading **{folder}** ...')
        all_datas = {}
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            num = file_path.split('/')[-1].split('.')[0]
            # st.markdown(num)
            if not file_path.endswith('json'):
                continue
            this_data = self.read_data(file_path)
            all_datas[num] = this_data
        return all_datas, folder

