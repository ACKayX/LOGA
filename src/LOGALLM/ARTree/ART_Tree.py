import json
import streamlit as st

from .ART_Node import ART_Node
from .ART_Updater import ART_Updater

class ART_Tree:
    def __init__(self):
        self.edges = []
        self.nodes = []
        self._trees = []
        self.updater = ART_Updater()

    def get_data(self, data):
        # st.markdown(data)
        self._data = data
        # 创建 ART_Node 
        for arg_id, args in data['Args'].items():
            attacks = args['attacks']
            nodes = [ART_Node(arg_id, attack) for attack in attacks]
            # 节点链接成树
            # st.markdown([str(node) for node in nodes])
            self.build(nodes)
            self._trees.append(nodes)
        # print(self._trees)


    def build(self, nodes):
        ids = [node.get_id() for node in nodes] # 一棵树的所有 id
        edges = [] # 一棵树的所有边
        gnodes = [] # 一棵树的所有节点的 node 结构
        visited = set()
        # nodes # 一棵树的所有节点
        for node in nodes[::-1]:
            if node.get_id() in visited:
                continue
            visited.add(node.get_id())

            for na in node.get_attack():
                na_key = list(na.keys())[0]
                attack_weight = na.get(na_key,0)
                # st.markdown(f"{na_key} - {attack_weight}")
                nodes[ids.index(na_key)].set_next(node,attack_weight)
            for nx in node.next:
                edges.append((nx.get_id(), node.get_id()))
            gnodes.append(node.node)
        # print(gnodes)
        self.edges.append(edges)
        self.nodes.append(gnodes)
        # st.markdown('FIN BUILD')

    
    def update(self, update):
        self._update = update
        root = ART_Node('Root', self.create_root())
        self.infos = {
            "root": root,
            "trees": self._trees,
            "judge": [],
            "edges": []
        }
        for tree in self._trees:
            tree_root = tree[0]
            self.update_node(tree_root)
            self.infos['judge'].append(self.judge(tree_root))
            self.infos['edges'].append((tree_root.get_id(), root.get_id()))

        return self.infos

    def create_root(self):
        root_data = {
            "id": "Claim",
            "text": self._data['claim'],
            "confidence": 1,
            "attacks": []
        }
        return root_data

    def update_node(self, node):
        # st.header(len(node))
        if hasattr(node, "next") and node.next:
            for child in node.next:
                if child:
                    self.update_node(child)

        # org_conf = node.get_conf()
        # node.update_gnode(1, org_conf)

        if len(node.next) > 0:
            CA = [{i: node.next[i]} for i in node.next if i.status == 1]
            CR = [{i: node.next[i]} for i in node.next if i.status == 2]
            # node.conf = self.update_way(CA, CR, node.conf)
            new_conf, status = self.updater[self._update](CA, CR, node.get_conf())
            # print(new_conf)

            node.update_gnode(1, node.get_conf())
            node.set_conf(new_conf)  # 直接修改 conf
            node.update_gnode(status, new_conf)

            # node.update_gnode(status, new_conf)
        else:
            node.update_gnode(1, node.get_conf())


    def judge(self, node):
        status = node.get_status()
        if status == 1:
            return 'Warranted'
        elif status == 2:
            return 'Unwarranted'
        elif status == 0:
            return 'Undecided'
