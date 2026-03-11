import json 
import streamlit as st

ID = "id"
CA = "cate"
TE = "text"
CONF = "confidence"
ATTK = "attacks"


class ART_Node:
    def __init__(self, num, data):
        self._id = f"{num}_{data[ID]}"
        if data[ID].startswith("A"):
            self.cate = data[CA]
        else: 
            self.cate = None
        self._text = data[TE]
        self._conf = float(data[CONF])
        self.attack = [
            {f'{num}_{n}': data[ATTK][n]} for n in data[ATTK]
        ]
        self.next = {}
        self.status = None 
        self.node = self.create_gnode()

    def create_gnode(self):
        this = {
            'id': self._id,
            'text': self._text,
            'conf': self._conf,
            'newconf': self._conf,
            'status': self.status,
            'cate': self.cate,
            'attack': self.attack
        }
        return this

    def update_gnode(self, status, conf):
        self._conf = conf
        self.node['newconf'] = conf
        self.status = status
        self.node['status'] = self.status

    def set_conf(self, conf):
        self._conf = conf
        self.node['cond'] = conf

    def show_node(self):
        st.markdown(f'{self._id} {self._conf}')
        if self.next:
            for n in self.next:
                n.show_node()

    def set_next(self, child, weight):
        self.next[child] = weight

    def get_id(self):
        return self._id

    def get_attack(self):
        return self.attack

    def set_conf(self, conf):
        self._conf = conf

    def get_conf(self):
        return self._conf
    
    def get_status(self):
        return self.status
    
    def get_text(self):
        return self._text

    def get_node(self):
        return self.node

    def get_argu(self):
        return self._text

    def __str__(self):
        return self._id