import os
import pandas as pd
import numpy as np
import streamlit as st

from .Page_Evaluation import Page_Evaluation
from .Base_page import Base_page
from ..Evaluator import Evaluator
from ..Reasoner import Reasoner
from ..Ranker import Ranker

class Page_CrossValidation(Base_page):
    def __init__(self):
        super().__init__("CrossValidation")

    def read_all_dataset(self):
        data_path = "./data"
        data_list = {
            i: os.path.join(data_path, i) for i in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,i)) and i != 'ELSE'
        }
        datasets = {}
        for i in data_list:
            path = data_list[i]
            datas,folder_path = super().read_full_dataset(path)
            datasets[i] = [datas, folder_path]
        return datasets

    def read_labels(self, path):
        path = os.path.join('./data',path)
        org_data = os.path.join(path,'data.json')
        data = super().read_data(org_data)
        org_labels = {}
        for i in data:
            org_labels[str(i['id'])] = i['label']
        return org_labels

    def process_dataset_item(self, num_str, label_val, data_val, folder_path_val, update_val):
        num = int(num_str)
        label = {'label':True} if label_val else {'label':False}
        info, result = super().step_tree_const(
            data_val,
            this_path=os.path.join(folder_path_val, f'{num_str}.json'),
            llm=self.llm,
            id=num_str,
            update=update_val
        )
        list_result = list(result.values())
        list_result.append(label)

        return {
            'label': label_val,
            'num': num,
            'info': info,
            'result': result,
        }

    def display_evaluation(self, res_sems, path):
        eva = Evaluator(res_sems)
        res_df = eva.eval(path)
        return res_df

    def cv_numbers(self, STEP):
        nums = []
        for i in range(200):
            nums.append(i)
            if len(nums) == STEP:
                yield nums
                nums = []

    def run_cv(self, update):
        st.markdown('---')
        datasets = self.read_all_dataset()
        STEP = 40
        for nums in self.cv_numbers(STEP):
            reasoner = Reasoner(nums)
            res_dfs = []
            for name in datasets:
                dataset, folder_path = datasets[name]

                '''
                dict_labels = {}
                all_infos = {}
                all_cond_res = {}
                labels = self.read_labels(name)
                for num_int in range(len(dataset)):
                    if num_int not in nums:
                        continue
                    num_str = str(num_int)
                    label_val = labels[num_str]
                    data_val = dataset[num_str]
                    res = self.process_dataset_item(num_str, label_val, data_val, folder_path, update)
                    num = res['num']
                    dict_labels[num] = res['label']
                    all_infos[num] = res['info']
                    all_cond_res[num] = res['result']
                df_conds = pd.DataFrame(all_cond_res).T
                reasoner.get_data(df_conds)
                reasoner.add_reasoner(reasoner.agg_threshold_True)
                reasoner.add_reasoner(reasoner.agg_veto)
                reasoner.add_reasoner(reasoner.agg_Wc_S)
                reasoner.add_reasoner(reasoner.agg_Wc_Ws)
                dict_sems = reasoner.get_results()
                label_series = pd.Series(dict_labels)
                dict_sems['label'] = label_series
                '''
                df_conds, dict_sems = self.reasoning(reasoner, update, name ,dataset, folder_path, skips=nums)
                res_dfs.append(self.display_evaluation(dict_sems, folder_path))
            df = pd.concat(res_dfs)
            st.dataframe(df)

    def reasoning(self, reasoner, update, name, dataset, folder_path, skips=None):
        dict_labels = {}
        all_infos = {}
        all_cond_res = {}
        labels = self.read_labels(name)
        keys = sorted(dataset.keys(), key=lambda x: int(x) if x.isdigit() else x)
        for num_str in keys:
            if skips is not None:
                if int(num_str) not in skips:
                    continue
            label_val = labels[num_str]
            data_val = dataset[num_str]
            res = self.process_dataset_item(num_str, label_val, data_val, folder_path, update)
            num = res['num']
            dict_labels[num] = res['label']
            all_infos[num] = res['info']
            all_cond_res[num] = res['result']
        df_conds = pd.DataFrame(all_cond_res).T
        # print(df_conds)
        reasoner.get_data(df_conds)
        '''------------ <Add Aggregation> ------------'''
        reasoner.add_reasoner(reasoner.agg_threshold_True)
        reasoner.add_reasoner(reasoner.agg_veto)
        reasoner.add_reasoner(reasoner.agg_Wc_S)
        reasoner.add_reasoner(reasoner.agg_Wc_Ws)
        dict_sems = reasoner.get_results()
        label_series = pd.Series(dict_labels)
        dict_sems['label'] = label_series
        return df_conds, dict_sems



    def run(self, llm):
        datasets = self.read_all_dataset()
        self.llm = llm
        reasoner = Reasoner()
        update = super().set_update()
        res_dfs = []
        for name in datasets:
            dataset, folder_path = datasets[name]
            df_conds, dict_sems = self.reasoning(reasoner, update, name, dataset, folder_path)
            res_dfs.append(self.display_evaluation(dict_sems ,folder_path))
        df = pd.concat(res_dfs)
        st.dataframe(df)
        self.run_cv(update)





