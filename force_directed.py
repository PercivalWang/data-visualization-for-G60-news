import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

# 1. 基础设置 ======================================================
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 2. 数据准备 =====================================================
# (替换为您的实际数据加载代码)
years = ['2122', '2223', '2324', '2425']
sample_data = {
    '2122': [('发展', 8676), ('长三角', 7189), ('企业', 6240), ('产业', 5868), ('创新', 5494)],
    '2223': [('发展', 8000), ('长三角', 7000), ('科创', 6500), ('产业', 6000), ('G60', 5500)],
    '2324': [('科创', 7500), ('G60', 7000), ('发展', 6800), ('长三角', 6500), ('一体化', 6000)],
    '2425': [('一体化', 8000), ('科创', 7800), ('G60', 7500), ('数字经济', 7000), ('发展', 6800)]
}

data = {}
for year in years:
    df = pd.DataFrame(sample_data[year], columns=['word', 'frequency'])
    data[year] = df.sort_values('frequency', ascending=False).head(5)

# 3. 创建网络图 ==================================================
G = nx.DiGraph()

# 添加节点
colors = cm.rainbow(np.linspace(0, 1, len(years)))
for i, year in enumerate(years):
    for _, row in data[year].iterrows():
        node_id = f"{row['word']}_{year}"
        G.add_node(node_id,
                   year=year,
                   word=row['word'],
                   frequency=row['frequency'],
                   color=colors[i])

# 添加边
for i in range(len(years) - 1):
    current_year = years[i]
    next_year = years[i + 1]

    # 相同词语延续
    common_words = set(data[current_year]['word']).intersection(set(data[next_year]['word']))
    for word in common_words:
        G.add_edge(f"{word}_{current_year}", f"{word}_{next_year}",
                   weight=2, style='solid', color='#1f78b4')

    # 同排名连接
    min_len = min(len(data[current_year]), len(data[next_year]))
    for rank in range(min_len):
        if data[current_year].iloc[rank]['word'] != data[next_year].iloc[rank]['word']:
            G.add_edge(
                f"{data[current_year].iloc[rank]['word']}_{current_year}",
                f"{data[next_year].iloc[rank]['word']}_{next_year}",
                weight=1, style='dashed', color='#a6cee3')

# 4. 手动布局设置 ================================================
# 基础位置 (可以调整这些坐标)
manual_positions = {
    # 格式: "词语_年份": (x坐标, y坐标)
    "发展_2122": (0, 2),
    "长三角_2122": (0, 1),
    "企业_2122": (0, 0),
    "产业_2122": (0, -1),
    "创新_2122": (0, -2),

    "发展_2223": (3, 2.2),
    "长三角_2223": (3, 1),
    "科创_2223": (3, 0),
    "产业_2223": (3, -1),
    "G60_2223": (3, -2),

    "科创_2324": (6, 2),
    "G60_2324": (6, 1),
    "发展_2324": (6, 0),
    "长三角_2324": (6, -1),
    "一体化_2324": (6, -2),

    "一体化_2425": (9, 2),
    "科创_2425": (9, 1),
    "G60_2425": (9, 0),
    "数字经济_2425": (9, -1),
    "发展_2425": (9, -2)
}

# 应用手动布局
pos = {}
for node in G.nodes():
    if node in manual_positions:
        pos[node] = manual_positions[node]
    else:
        # 默认位置 (如果没有手动指定)
        year = G.nodes[node]['year']
        year_idx = years.index(year)
        pos[node] = (year_idx * 3, 0)  # 默认按年份等距排列

# 5. 可视化参数设置 ==============================================
plt.figure(figsize=(16, 10))

# 节点设置 (可调整参数)
node_size_multiplier = 0.8  # 节点大小乘数
node_sizes = [np.log(G.nodes[n]['frequency']) * 80 * node_size_multiplier for n in G.nodes()]

# 边设置 (可调整参数)
edge_width_solid = 1.5  # 实线边宽度
edge_width_dashed = 1.0  # 虚线边宽度
arrow_size = 15  # 箭头大小

# 6. 绘制图形 ===================================================
# 绘制边
solid_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['style'] == 'solid']
dashed_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['style'] == 'dashed']

nx.draw_networkx_edges(G, pos, edgelist=solid_edges,
                       edge_color='#1f78b4',
                       width=edge_width_solid,
                       arrowstyle='->',
                       arrowsize=arrow_size,
                       alpha=0.8)

nx.draw_networkx_edges(G, pos, edgelist=dashed_edges,
                       edge_color='#a6cee3',
                       width=edge_width_dashed,
                       style='dashed',
                       arrowstyle='->',
                       arrowsize=arrow_size - 5,
                       alpha=0.6)

# 绘制节点
node_colors = [G.nodes[n]['color'] for n in G.nodes()]
nodes = nx.draw_networkx_nodes(G, pos,
                               node_color=node_colors,
                               node_size=node_sizes,
                               alpha=0.9,
                               edgecolors='white',
                               linewidths=0.8)

# 绘制标签 (可调整参数)
label_offset = 0.3  # 标签垂直偏移量
labels = {n: G.nodes[n]['word'] for n in G.nodes()}
label_pos = {k: (v[0], v[1] + label_offset) for k, v in pos.items()}

nx.draw_networkx_labels(G, label_pos, labels,
                        font_size=10,
                        font_family='SimHei',
                        font_weight='bold',
                        bbox=dict(facecolor='white',
                                  edgecolor='none',
                                  alpha=0.7,
                                  boxstyle='round,pad=0.2'))

# 7. 添加装饰元素 ================================================
# 添加年份标记 (可调整位置)
for i, year in enumerate(years):
    plt.text(i * 3, 3.5,  # x,y坐标
             f"20{year[:2]}-20{year[2:]}年",
             ha='center',
             fontsize=12,
             bbox=dict(facecolor='white', alpha=0.8))

# 添加图例
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], color='#1f78b4', lw=2, label='same word'),
    Line2D([0], [0], color='#a6cee3', lw=2, linestyle='--', label='row')
]
plt.legend(handles=legend_elements, loc='upper right')

plt.title("force-directed network", fontsize=14)
plt.xlim(-2, 11)  # 调整x轴范围
plt.ylim(-3.5, 4)  # 调整y轴范围
plt.axis('off')

plt.tight_layout()
plt.savefig('C:/Users/w1782/Desktop/大一下作业/数据可视化作业/dataset/picture/force_directed.png')
plt.show()






# import pandas as pd
# import networkx as nx
# from pyvis.network import Network
# from gen_net import generate_undirected_graph, detect_communities
#
# # 1. 加载四个年份的词频数据
# years = ['2122', '2223', '2324', '2425']
# file_paths = [f"C:/Users/w1782/Desktop/大一下作业/数据可视化作业/dataset/newdata/{year}_t_f.csv" for year in years]
# dfs = [pd.read_csv(fp, encoding='utf-8-sig') for fp in file_paths]
#
# # 2. 提取每个年份前20的热点词汇
# top_n = 20
# hot_words = set()
# for i, (year, df) in enumerate(zip(years, dfs)):  # 同时遍历years和dfs
#     top_words = df.nlargest(top_n, 'frequency')['word'].tolist()
#     hot_words.update(top_words)
#     print(f"20{year[:2]}-20{year[2:]}: {', '.join(top_words[:5])}...")
#
# # 3. 构建跨年度有向网络（从早年到晚年）
# G = nx.DiGraph()
# year_pairs = [(0, 1), (1, 2), (2, 3)]  # 年份连接顺序：21-22→22-23→23-24
#
# for src, tgt in year_pairs:
#     src_year = years[src]
#     tgt_year = years[tgt]
#     src_df = dfs[src]
#     tgt_df = dfs[tgt]
#
#     # 只保留热点词汇的共现关系
#     for word in hot_words:
#         if word in src_df['word'].values and word in tgt_df['word'].values:
#             # 边的权重取目标年份的词频（表示发展趋势）
#             weight = tgt_df[tgt_df['word'] == word]['frequency'].values[0]
#             G.add_edge(f"20{src_year[:2]}_{word}", f"20{tgt_year[:2]}_{word}",
#                        weight=weight,
#                        title=f"{word}<br>20{src_year[:2]}→20{tgt_year[:2]}<br>频次: {weight}")
#
# # 4. 使用gen_net的社区检测功能（需先转为无向图）
# undirected_G = G.to_undirected()
# partition = detect_communities(undirected_G)
#
# # 5. 创建可视化网络
# net = Network(
#     height="800px",
#     width="100%",
#     directed=True,
#     bgcolor="#FFFFFF",
#     font_color="black"
# )
#
# # 社区颜色映射
# community_colors = {
#     0: '#FF9999',  # 产业类
#     1: '#66B2FF',  # 技术类
#     2: '#99FF99',  # 资本类
#     3: '#FFD700'   # 其他类
# }
#
# # 6. 添加节点（按社区着色）
# for node in G.nodes():
#     year, word = node.split('_', 1)
#     comm_id = partition.get(word, 3) % 4  # 默认其他类
#     net.add_node(
#         node,
#         label=word,
#         title=f"{word} ({year})<br>社区: {['产业', '技术', '资本', '其他'][comm_id]}",
#         color=community_colors[comm_id],
#         size=15 + G.out_degree(node, weight='weight') * 0.1,  # 按出度权重缩放
#         group=comm_id
#     )
#
# # 7. 添加带箭头的边
# for edge in G.edges(data=True):
#     net.add_edge(
#         edge[0], edge[1],
#         value=edge[2]['weight'] * 0.1,  # 边粗细
#         title=edge[2]['title'],
#         arrowStrikethrough=False,
#         smooth={"type": "curvedCW", "roundness": 0.2}  # 曲线箭头
#     )
#
# # 8. 力导向布局配置
# physics_options = """
# {
#     "forceAtlas2Based": {
#         "gravitationalConstant": -50,
#         "centralGravity": 0.01,
#         "springLength": 150,
#         "springConstant": 0.08,
#         "damping": 0.4,
#         "avoidOverlap": 0.1
#     },
#     "minVelocity": 0.75,
#     "solver": "forceAtlas2Based"
# }
# """
#
# # 设置选项以支持中文显示
# net.set_options(physics_options)
# net.set_options("""
# var options = {
#     "nodes": {
#         "font": {
#             "face": "微软雅黑"
#         }
#     }
# }
# """)
#
# # 9. 保存并展示
# output_file = "g60_temporal_network.html"
# net.show(output_file, notebook=False)
# print(f"可视化已保存至: {output_file}")






# import pandas as pd
# import networkx as nx
# from pyvis.network import Network
# from gen_net import generate_undirected_graph, detect_communities
#
# # 1. 加载数据（示例路径，请替换为实际路径）
# df_matrix = pd.read_csv(r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2122_matrix_article.csv")
#
# # 2. 生成无向图并检测社区
# G = generate_undirected_graph(df_matrix)
# partition = detect_communities(G)
#
#
# # 5. 可选：生成交互式Pyvis可视化
# def generate_interactive_network(G, partition):
#     net = Network(height="800px", width="100%", notebook=False)
#
#     # 设置字体以支持中文显示
#     net.set_options("""
#         var options = {
#             "nodes": {
#                 "font": {
#                     "face": "微软雅黑"
#                 }
#             },
#             "physics": {
#                 "forceAtlas2Based": {
#                     "gravitationalConstant": -50,
#                     "centralGravity": 0.01,
#                     "springLength": 150,
#                     "springConstant": 0.08,
#                     "avoidOverlap": 1
#                 },
#                 "minVelocity": 0.75,
#                 "solver": "forceAtlas2Based"
#             }
#         }
#     """)
#
#     # 社区颜色映射（与静态图一致）
#     community_colors = [
#         "#FF9999", "#66B2FF", "#99FF99", "#FFD700",
#         "#FF6B6B", "#4ECDC4", "#FFA07A", "#20B2AA"
#     ]
#
#     # 添加节点
#     weighted_degree = {node: sum(d["weight"] for _, d in G[node].items()) for node in G.nodes}
#     max_weight = max(weighted_degree.values())
#
#     for node in G.nodes():
#         net.add_node(
#             node,
#             size=10 + 30 * (weighted_degree[node] / max_weight),
#             color=community_colors[partition[node] % len(community_colors)],
#             title=f"{node}<br>Community: {partition[node]}<br>Weighted Degree: {weighted_degree[node]:.1f}"
#         )
#
#     # 添加边
#     for u, v, d in G.edges(data=True):
#         net.add_edge(u, v, value=d['weight'] * 0.5)
#
#     # 物理布局配置
#     net.show_buttons(filter_=['physics'])
#
#     # 保存为HTML
#     net.show("interactive_network.html")
#
#
# generate_interactive_network(G, partition)












