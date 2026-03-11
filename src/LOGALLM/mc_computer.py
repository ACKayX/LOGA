import os
import json
import yaml
import itertools
import networkx as nx

class MC_Computer:
    def __init__(self):
        self.cmatrix = None
        self.conflicts = None
        self.nodes = None


    def read_conflict_file(self, path):
        # conflict_file = "./config/conflict_text.json" # 测试文件
        conflict_file = path
        with open(conflict_file, 'r') as f:
            data = json.load(f)
        # print(data)
        self.cmatrix = data

    def get_conflict_pair(self):
        conflict_pair = []
        nodes = set()
        for i in self.cmatrix:
            arg1 = i['node1']
            arg2 = i['node2']
            if arg1 not in nodes:
                nodes.add(arg1)
            if arg2 not in nodes:
                nodes.add(arg2)
            if i['conflict'] == 1:
                conflict_pair.append((arg1, arg2))

        # print(conflict_pair)
        self.conflicts = conflict_pair
        self.nodes = nodes


    def build_graph(self):

        G = nx.Graph()

        G.add_nodes_from(list(self.nodes))

        G.add_edges_from(self.conflicts)
        self.graph = G

    def compute_MCS(self):
        # mcs_list = list(nx.find_maximal_independent_sets(self.graph))
        # mcs_list = list(nx.find_cliques(self.graph))
        mcs_list = list(nx.maximal_independent_set(self.graph))
        print(mcs_list)
        for i, mcs in enumerate(mcs_list, 1):
            print(f"MCS {sorted(mcs)}")

    def _is_conflict_free(self, subset):
        '''
        to test if there is an edge(conflict) between each nodes
        '''
        for u, v in itertools.combinations(subset, 2):
            if self.graph.has_edge(u, v):
                return False
        return True

    def _is_maximal(self, subset_set):
        for v in self.nodes:
            if v in subset_set:
                continue

            OK = True
            for u in subset_set:
                if self.graph.has_edge(u, v):
                    OK = False
                    break
            if OK:
                return False
        return True


    def compute_MC_sets(self):
        mc_sets = []
        n = len(self.nodes)  # number of nodes(T)
        # print(self.nodes)
        if len(self.conflicts) == 0:
            return [set(self.nodes)]

        for r in range(n):
            for comb in itertools.combinations(self.nodes, r):
                if not self._is_conflict_free(comb):
                    continue
                s = set(comb)
                if self._is_maximal(s):
                    mc_sets.append(tuple(sorted(s)))
        mc_sets = sorted(set(mc_sets), key=lambda x: (-len(x), x))
        return mc_sets
