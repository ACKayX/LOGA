import streamlit as st
import graphviz


class ART_Viser:
    def __init__(self, data):
        self.data = data
        st.subheader('ART Forest Visualisation')

    def _create_graph(self, rankdir='TB'):
        """创建并配置图的通用方法"""
        graph = graphviz.Digraph()
        graph.attr(rankdir=rankdir)
        graph.attr('node', shape='box', style='filled', fillcolor='lightblue',
            fontname='Microsoft YaHei', fontsize='12')
        graph.attr('edge', color='#4A90E2', arrowsize='0.8')
        return graph

    def draw(self):
        """绘制整个森林"""
        roots = self.data['trees']
        st.markdown(self.data['root'].get_node()['text'])
        with st.expander(f"Roots", expanded=True):
            self.draw_trees_to_root()

        for i, tree in enumerate(roots):
            with st.expander(f"Tree {i+1}", expanded=False):
                st.markdown(f"### Tree {i + 1}")
                self.draw_tree(tree)
                # st.divider()  # 添加分隔线

    def draw_trees_to_root(self):
        """绘制根节点和所有树的根节点连接"""
        graph = self._create_graph()

        root_data = self.data['root'].get_node()
        root_info = f"{root_data['id']}"
        graph.node('Root_Claim', root_info)

        # 添加每棵树的根节点
        for i, tree in enumerate(self.data['trees']):
            root_node = tree[0]
            info = root_node.get_node()
            node_id = f"tree_{i}_{info['id']}"
            tinfo = self._format_node_label(info)
            tinfo += f"\\ncate: {info['cate']}"
            graph.node(node_id, tinfo)
            graph.edge('Root_Claim', node_id)

        st.graphviz_chart(graph)


    def draw_tree(self, tree):
        """绘制单棵树的完整结构，并展示节点信息"""
        # with st.expander("Tree View", expanded=True):
        col1, col2 = st.columns([4, 6])

        # -------- 左侧：绘制 Graph --------
        with col1:
            graph = self._create_graph(rankdir='BT')

            all_nodes = {}
            all_edges = []

            # 收集节点和边
            for node in tree[::-1]:
                info = node.get_node()
                node_id = str(info['id'])
                all_nodes[node_id] = info

                if 'attack' in info and info['attack']:
                    for attack_item in info['attack']:
                        target_id = str(list(attack_item.keys())[0])
                        all_edges.append((node_id, target_id))

            # 添加所有节点
            for node_id, node_data in all_nodes.items():
                label = self._format_node_label(node_data)
                graph.node(node_id, label)

            # 添加所有边
            for from_id, to_id in all_edges:
                graph.edge(from_id, to_id)

            # 显示图
            st.graphviz_chart(graph, use_container_width=True)

        # -------- 右侧：展示节点详情 --------
        with col2:
            # st.markdown("### Content")
            # st.markdown(type(all_nodes.items()))
            for node_id, node_data in reversed(all_nodes.items()):
                st.markdown(
                    f"- **ID**: {node_data['id']}\t **Status**: {node_data['status']}  \n "
                    f"  **Conf**: {node_data['conf']:.2f} ➡️ {node_data.get('newconf', node_data['conf']):.2f}  \n"
                    f"  **Text**: {node_data['text']}"
                )



    # def draw_box(self, data):
    #     """绘制单个节点（独立的图）"""
    #     graph = self._create_graph()
    #
    #     label = self._format_node_label(data)
    #     graph.node(data['id'], label)
    #
    #     st.graphviz_chart(graph)

    def _format_node_label(self, data):
        """格式化节点标签"""
        return f"ID: {data['id']}\\nConf: {data['conf']:.2f} ➡️ {data.get('newconf', data['conf']):.2f}\\nStatus: {data['status']}"