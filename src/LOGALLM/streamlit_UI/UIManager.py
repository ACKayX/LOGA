import json
import streamlit as st
from .Page_DemoSingle import Page_DemoSingle
from .Page_Evaluation import Page_Evaluation
from .Page_CrossValidation import Page_CrossValidation
from .Base_page import Base_page
from ..LLM_Manager import *

class UIManager:
    def __init__(self):
        st.set_page_config(
            page_title="LOGALLM",
            layout="wide"
        )
        # st.title('LoGicArgLLM UI Page')
        self.pages = {
            'DemoSingle': Page_DemoSingle,
            'Evaluation': Page_Evaluation,
            'CV': Page_CrossValidation
        }

    def choose_llm(self):
        llms_configs_path = "./configs/llms.json"
        with open(llms_configs_path, 'r') as f:
            llms_dict = json.loads(f.read())
        # print(llms)
        llms_list = list(llms_dict.values())

        st.sidebar.header('Set LLM')
        llm_option = [
            "deepseek",
            *llms_list
        ]
        llm_choice = st.sidebar.radio(
            'select llm to use',
            options=llm_option
        )
        if llm_choice == "deepseek":
            llm = DS_manager()
        else:
            llm = Sflow_manager()
        return llm

    def run(self):
        st.sidebar.header('Page Mode')
        page_names = list(self.pages.keys())
        page_choice = st.sidebar.radio(
            "Page",
            options=page_names,
        )
        llm = self.choose_llm()
        current_page = self.pages.get(page_choice)
        if current_page:
            current_page_i = current_page()
            current_page_i.run(llm)
        else:
            st.error("Wrong PAGE!")


