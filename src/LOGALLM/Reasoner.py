from re import search
from unittest.mock import inplace

import streamlit as st
import pandas as pd
import numpy as np

from .ARTree import *
from .Ranker import Ranker

NB_Semantic = 16

class Reasoner:
    def __init__(self, skip=None):
        self.nb = NB_Semantic
        self.data = None
        self.ranker = Ranker(skip)
        # self.skip = skip

    def get_label(self, labels):
        self.labels = labels

    def get_data(self, data):
        self.data = data
        self.reason_semantics()

    def get_results(self):
        return self.results

    def get_semantics(self):
        semantics = {
            '15': [0, 1, 3],
            '16': [0, 2, 3],
            '17a': [2, 3, 4],
            '17e': [1, 3, 4],
            '18': [1, 3, 4, 5],
            '19': [3, 4, 6],
            '20': [3, 4, 7],
            '21': [3, 4, 8],
            '22': [3, 4, 9, 10],
            's': [3, 11],
            'p': [3, 12],
            'm': [3, 13],
            'sp': [3, 11, 12],
            'sm': [3, 11, 13],
            'pm': [3, 12, 13],
            'spm': [3, 11, 12, 13]
        }
        return semantics

    def reason_semantics(self):
        semantics = self.get_semantics()
        cols = self.data.columns
        # st.markdown(self.data.shape)
        results = {}
        # self.data = DataFrame

        for i in semantics:
            cond_str = semantics[i]
            conds = [cols[i] for i in cond_str]
            results[i] = self.data[conds].all(axis=1)
        # st.dataframe(pd.DataFrame(results))
        self.results = pd.DataFrame(results)

        # return results

    def add_reasoner(self, function_name):

        # st.markdown(function_name)
        values = function_name()
        func_name = '_'.join(function_name.__name__.split('_')[1:])
        # print(f'<Add Aggregation Reasoner {func_name}>')
        self.results[func_name] = values

    def agg_threshold_True(self, threshold=0.5):
        tts = []
        for key in self.results:
            tt = sum(self.results[key])
            if tt == 0 or tt == self.results.shape[0]:
                tts.append(key)
        data = self.results.copy()
        # st.dataframe(data)
        [data.drop(i,inplace=True, axis=1) for i in tts]
        true_counts = data.sum(axis=1)
        cTrue = (true_counts / self.nb) > threshold
        # print(type(cTrue))
        return cTrue

    def agg_veto(self, VNumber=5):
        weights = self.ranker.collect_weights(self.ranker.ws)
        sorted_sems = self.ranker.sort_dict(weights)[:-VNumber]
        # print(sorted_sems)
        cols_names = [key for key, _ in sorted_sems]
        # print(cols_names)
        data = self.results.copy().T.loc[cols_names].T
        # print(data)
        # st.dataframe(data)
        length = len(cols_names)
        true_counts = data.sum(axis=1)
        isTrue = true_counts > (length/2)
        return isTrue

    def calcul_cond_weights(self):
        '''
        按照 ranker 中每个 condition 的分数, 将每个 semantic 的 contdition 的分数归一化, 然后得到每个 condition 的权重
        '''
        weights = self.ranker.collect_weights(self.ranker.wc)
        # print(f'weights = {weights}')

        dict_conds_weights = {w:weights[w] for w in weights}
        semantics = self.get_semantics()
        keys = list(dict_conds_weights.keys())
        sem_keys = list(semantics.keys())
        condition_weights = {}
        for semantic in semantics:
            conditions = semantics[semantic]
            # print(conditions)
            conds_weghts = [dict_conds_weights[keys[cond]] for cond in conditions]
            cw_sum = sum(conds_weghts)
            # print(cw_sum)
            if cw_sum != 0:
                # print( f'condsweights= {conds_weghts}')
                condition_weights[semantic] = [float(w/cw_sum) for w in conds_weghts]
                # print(f'inlist = {condition_weights[semantic]}')
            else :
                condition_weights[semantic] = [0 for w in conds_weghts]
        self.cond_weights = condition_weights

    def get_cond_weights(self, semantic):
        values = self.cond_weights[semantic]
        return values

    def agg_Wc_S(self):

        self.calcul_cond_weights()
        semantics = self.get_semantics()
        conds_name = list(self.data.keys())

        data = pd.DataFrame(self.data).T
        all_values = []
        for line in data:
            the_dict = data[line].astype(int).to_dict()
            this_sums = []
            for key in semantics:
                # print(key,type(key))
                cond_weights = self.get_cond_weights(key) #
                condition_this_sem = semantics[key]
                this_sum = sum([i*the_dict[conds_name[j]] for i,j in zip(cond_weights,condition_this_sem)])
                this_sums.append(this_sum)
            all_values.append(sum(this_sums))

        vv = np.mean(all_values)
        return_values = {}
        for key, value in zip(data,all_values):
            if value >= vv :
                return_values[key] = True
            else:
                return_values[key] = False

        # print(all_values)
        # return pd.Series(all_values >= np.median(all_values))
        pred_series = pd.Series(return_values)
        return pred_series.astype(bool)

    def calcul_sems_weights(self):
        weights_sems = self.ranker.collect_weights(self.ranker.ws)
        # print(weights_sems)
        weights = [weights_sems[i] for i in weights_sems]
        sum_weights = sum(weights)
        w_sems = {i:weights_sems[i]/sum_weights for i in weights_sems}
        self.sems_weights = w_sems

    def get_sem_weights(self, semantic):
        if semantic == '22': return 0
        return self.sems_weights[semantic]

    def agg_Wc_Ws(self):
        self.calcul_sems_weights()
        self.calcul_cond_weights()
        semantics = self.get_semantics()
        conds_name = list(self.data.keys())
        data = pd.DataFrame(self.data).T
        all_values = []
        for line in data:
            the_dict = data[line].astype(int).to_dict()
            this_sums = []
            for key in semantics:
                # print(key)
                cond_weights = self.get_cond_weights(key) #
                # print(cond_weights)
                condition_this_sem = semantics[key]

                this_sum = sum([i*the_dict[conds_name[j]] for i,j in zip(cond_weights,condition_this_sem)])
                # print(f'sum = {this_sum}')
                '''和 Wc_S 的区别  在对语义求和时, 使用了每个语义的权重(根据语义的正确数量排序得到)'''
                # print(self.get_sem_weights(key))
                this_sums.append(this_sum * self.get_sem_weights(key))
            all_values.append(sum(this_sums))

        s = pd.Series(all_values)
        vv = s.median()
        return_values = {}

        for value,key in zip(all_values,data):

            if value >= vv:
                return_values[key] = True
            else:
                # ff.append(int(value < vv))
                return_values[key] = False

        pred_series = pd.Series(return_values)
        return pred_series.astype(bool)
