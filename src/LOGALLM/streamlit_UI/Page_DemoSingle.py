import os
import json

import streamlit as st
import pandas as pd

from .Base_page import Base_page
from ..ARTree.ART_Viser import ART_Viser
from ..Argument_Generator import Argument_Generator
from ..ARTree import *
from ..Reasoner import Reasoner

NB_Sems = 16
DF_HEDERS = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 's', 'p', 'm']

class Page_DemoSingle(Base_page):
    def __init__(self):
        self.path = "./data/ELSE/"
        self.this_path = None
        self.number = None
        super().__init__("DemoSingle")

    def run(self, llm, update=None):
        self.llm = llm

        # 初始化 session_state
        if 'claim_submitted' not in st.session_state:
            st.session_state.claim_submitted = False
        if 'selected_claim_data' not in st.session_state:
            st.session_state.selected_claim_data = None

        mode = st.radio(
            "Choose mode:",
            options=["Select Existing Claim", "Create New Claim"],
            key="mode_selector"  # 添加 key
        )

        if mode == "Select Existing Claim":
            result = self.select_claim()
            if result:
                st.session_state.claim_submitted = True
                st.session_state.selected_claim_data = result
            elif not st.session_state.claim_submitted:
                st.stop()

        else:  # Create New Claim
            result = self.new_claim()
            if result:
                st.session_state.claim_submitted = True
                st.session_state.selected_claim_data = result
            elif not st.session_state.claim_submitted:
                st.stop()

        if st.session_state.claim_submitted and st.session_state.selected_claim_data:
            self.number, output, self.this_path = st.session_state.selected_claim_data

            update = super().set_update()
            infos, result = super().step_tree_const(
                output,
                this_path=self.this_path,
                llm=self.llm,
                id=self.number,
                update=update
            )

            list_result = list(result.values())
            data = pd.DataFrame([list_result], columns=DF_HEDERS)
            reasoner = Reasoner()
            reasoner.get_data(data)
            self.set_reasoner(reasoner)
            sem_result = reasoner.get_results()
            cond_res_df = pd.DataFrame([result])

            st.subheader('Condition Results')
            st.dataframe(cond_res_df)
            st.subheader('Semantic Results')
            st.dataframe(sem_result)
            self.step_vis_artrees(infos)

    def select_claim(self):
        dataset = super().get_list_dataset()
        dataset_name = dataset.split('/')[-1]
        all_datas, folder = super().read_full_dataset(dataset)
        keys = sorted(all_datas.keys(), key=lambda x: int(x) if x.isdigit() else x)
        claims_exists = [f'{k} - {all_datas[k]["claim"]}' for k in keys]

        num_claim = st.selectbox(
            f'select claim from {dataset}',
            options=claims_exists,
            key="claim_selector"
        )

        if st.button(f"Submit exists - {dataset_name}"):
            num = num_claim.split(' - ')[0]
            return num, all_datas[num], folder
        return None

    def new_claim(self):
        st.markdown("Demo claim will be save in ELSE folder")
        claim = st.text_input("Input Claim", key="new_claim_input")

        if st.button("Submit New"):
            if claim:
                ag = Argument_Generator(self.llm)
                output = ag.get_arguments(claim)
                nb_files = len(os.listdir(self.path))
                this_path = os.path.join(self.path, f'{str(nb_files)}.json')
                super().save_json(output, this_path)
                st.markdown(f'Data saved in {this_path}')
                return nb_files, output, this_path
            else:
                st.warning("Please enter a claim")
        return None


    def set_reasoner(self, reasoner):
        reasoner.add_reasoner(reasoner.agg_veto)
        reasoner.add_reasoner(reasoner.agg_threshold_True)
        reasoner.add_reasoner(reasoner.agg_Wc_S)
        reasoner.add_reasoner(reasoner.agg_Wc_Ws)


    def step_vis_artrees(self,infos):
        artv = ART_Viser(infos)
        artv.draw()
