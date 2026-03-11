import concurrent.futures
import os
from .Base_page import Base_page
import streamlit as st
import pandas as pd
import time

from ..Evaluator import Evaluator
from ..Reasoner import Reasoner
from ..Ranker import Ranker

import threading # 多线程
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 8

class Page_Evaluation(Base_page):
    def __init__(self):
        super().__init__("Evaluation")

    def process_dataset_item(self,num_str, label_val, data_val,folder_path_val, update_val):
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


    def run(self, llm, update=None):
        the_dataset = self.get_list_dataset()
        self.llm = llm
        labels = self.read_labels(the_dataset)
        # print(labels)
        datasets, folder_path = self.read_full_dataset(the_dataset)
        # datasets, folder_path = super().read_full_dataset(the_dataset)
        # print(datasets)
        update = super().set_update()
        all_results = {}
        all_infos = {}
        all_cond_res = {}
        reasoner = Reasoner()
        # start_time = time.time()
        dict_labels = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            # print(datasets)
            # for num_int in range(len(datasets)):
            for idx,num_int in enumerate(datasets):
                # print(datasets[num_int])
                # print(num_int)
                num_str = str(num_int)


                label_val = labels[num_str]
                # print(label_val)
                # dict_labels[int(num_str)] = label_val
                # print()
                try:
                    data_val = datasets[num_str]
                except KeyError as e:
                    print(f"KeyError {num_str}")
                    continue


                future = executor.submit(
                    self.process_dataset_item,
                    num_str,
                    label_val,
                    data_val,
                    folder_path,  # 假设 folder_path 不变
                    update,  # 假设 update 不变

                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    num = res['num']
                    dict_labels[num] = res['label']
                    all_infos[num] = res['info']
                    all_cond_res[num] = res['result']
                except Exception as exc:
                    # print(res['num'])
                    # print(f'Error in {exc.}')
                    print(f'Error in {exc}')
        df_conds = pd.DataFrame(all_cond_res).T
        reasoner.get_data(df_conds)
        '''------------ <Add Aggregation> ------------'''
        reasoner.add_reasoner(reasoner.agg_threshold_True)
        reasoner.add_reasoner(reasoner.agg_veto)
        reasoner.add_reasoner(reasoner.agg_Wc_S)
        reasoner.add_reasoner(reasoner.agg_Wc_Ws)

        dict_sems = reasoner.get_results()
        end_time = time.time()

        label_series = pd.Series(dict_labels)
        dict_sems['label'] = label_series

        # reasoner

        self.display_evaluation(df_conds, dict_sems, folder_path)

    def display_evaluation(self, res_cond,res_sems, path):
        eva = Evaluator(res_sems)
        df_cond_res = res_cond.add_suffix('_cond')
        # df_all = pd.concat((df_cond_res, res_sems), axis=1).sort_index()
        df_all = pd.concat((df_cond_res, res_sems), axis=1)
        df_all = df_all.sort_index()
        st.dataframe(df_all)
        dataset_name = path.split('/')[-2]
        if st.button('SAVE RESULT'):
            save_path = os.path.join('./result/', f'{dataset_name}.csv')
            df_all.to_csv(save_path)
            st.markdown(f'Dataframe saved in {save_path}')
            print(f'Dataframe saved in {save_path}')
        res_df = eva.eval(path)
        st.dataframe(res_df)

    def read_labels(self, path):
        org_data = os.path.join(path,'data.json')
        print("reading labels")
        data = super().read_data(org_data)
        org_labels = {}
        for i in data:
            # print(type(i['label']))
            if isinstance(i['label'], str):
                if i['label'] == 'true': org_labels[str(i['id'])] = True
                else:
                    org_labels[str(i['id'])] = False
            else:

                org_labels[str(i['id'])] = i['label']
        return org_labels

