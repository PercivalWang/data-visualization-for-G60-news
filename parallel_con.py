import pandas as pd
import numpy as np
import plotly.graph_objects as go
from gen_net import generate_undirected_graph, detect_communities
import plotly.express as px

# 定义年份列表
years = ['2122', '2223', '2324', '2425']

# 存储每个年份的数据和分区信息
dataframes = {}
partitions = {}

# 读取数据并生成社区划分
for year in years:
    file_path = f"C:/Users/w1782/Desktop/大一下作业/数据可视化作业/dataset/newdata/{year}_matrix_article.csv"
    dataframes[year] = pd.read_csv(file_path)

    # 生成无向图并检测社区
    G = generate_undirected_graph(dataframes[year])
    partitions[year] = detect_communities(G)

    # 标准化社区ID为0,1,2
    unique_ids = sorted(set(partitions[year].values()))
    id_mapping = {old: new for new, old in enumerate(unique_ids)}
    partitions[year] = {k: id_mapping[v] for k, v in partitions[year].items()}

# 创建节点数据
entity_data = {}
for year in years:
    data = dataframes[year]
    partition = partitions[year]

    for entity in data['Entity1'].unique():
        total_cooccurrence = data[(data['Entity1'] == entity) | (data['Entity2'] == entity)]['CoOccurrence'].sum()
        size = min(4 + total_cooccurrence * 0.4, 10)

        community_id = partition.get(entity, -1)

        if entity not in entity_data:
            entity_data[entity] = {
                'sizes': {year: size},
                'communities': {year: community_id}
            }
        else:
            entity_data[entity]['sizes'][year] = size
            entity_data[entity]['communities'][year] = community_id

# 将节点数据转换为DataFrame
entities = []
sizes = {year: [] for year in years}
communities = {year: [] for year in years}

for entity, data in entity_data.items():
    entities.append(entity)
    for year in years:
        sizes[year].append(data['sizes'].get(year, 0))
        communities[year].append(data['communities'].get(year, -1))

df = pd.DataFrame({
    'entity': entities,
    **{f'size_{year}': sizes[year] for year in years},
    **{f'community_{year}': communities[year] for year in years}
})

# 定义3个社区的颜色
community_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # 蓝、橙、绿

# 创建图例项
# 定义社区名称映射
community_names = {
    0: "技术",
    1: "资本",
    2: "产业"
}

# 创建图例项
legend_items = [
    go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=community_names[i],  # 使用映射后的名称
        showlegend=True
    ) for i, color in enumerate(community_colors)
]

# 创建平行集图
fig = go.Figure()

# 添加平行集图（修正了line参数）
fig.add_trace(go.Parcats(
    dimensions=[
        {'label': f'20{year[:2]}-20{year[2:]}',
         'values': df[f'community_{year}'],
         'categoryarray': [0, 1, 2]  # 强制只显示3个社区
         } for year in years
    ],
    line={
        'color': [community_colors[cid] if cid in [0, 1, 2] else '#CCCCCC'
                  for cid in df[f'community_{years[0]}']],
        'shape': 'hspline'
    },
    counts=[10] * len(df),  # 控制线条粗细的替代方案
    labelfont={'size': 14, 'family': 'SimHei'},
    tickfont={'size': 12, 'family': 'SimHei'},
    arrangement='freeform'
))

# 添加图例项
for item in legend_items:
    fig.add_trace(item)

# 设置布局
fig.update_layout(
    title={
        'text': 'G60 communities evolution (2021-2025)',
        'y': 0.95,
        'x': 0.5,
        'font': {'size': 20, 'family': 'SimHei'}
    },
    width=1200,
    height=800,
    margin=dict(l=80, r=80, b=120, t=100),
    paper_bgcolor='white',
    plot_bgcolor='white',
    legend=dict(
        title='社区分类',
        orientation='h',
        yanchor='bottom',
        y=-0.15,
        xanchor='center',
        x=0.5
    )
)

# # 添加注释
# fig.add_annotation(
#     x=0.5,
#     y=-0.25,
#     text="注：线条颜色表示实体所属社区，仅展示3个主要社区分类",
#     showarrow=False,
#     font={'size': 12, 'family': 'SimHei'}
# )

fig.show(renderer="browser")
fig.write_html("g60_community_evolution.html")


# 平行集图绘制方案

# import pandas as pd
# import plotly.graph_objects as go
# from gen_net import generate_undirected_graph, detect_communities
# import plotly.express as px
#
# # 定义年份列表
# years = ['2122', '2223', '2324', '2425']
#
# # 存储每个年份的数据和分区信息
# dataframes = {}
# partitions = {}
#
# def create_network_from_freq(df_freq, top_n=50):
#     """从词频数据创建网络图（使用gen_net.py的函数）"""
#     print(f"正在构建网络（使用前{top_n}个高频词）...")
#
#     # 创建边列表（模拟共现关系）
#     edges = []
#     words = df_freq.head(top_n)['word'].tolist()
#     freqs = df_freq.head(top_n)['frequency'].tolist()
#
#     # 创建全连接网络（权重为词频乘积）
#     for i in range(len(words)):
#         for j in range(i + 1, len(words)):
#             edges.append({
#                 "Entity1": words[i],
#                 "Entity2": words[j],
#                 "CoOccurrence": freqs[i] * freqs[j]
#             })
#
#     # 创建DataFrame模拟原始输入格式
#     df_matrix = pd.DataFrame(edges)
#     return df_matrix
#
# # 读取数据并生成社区划分
# for year in years:
#     file_path = fr"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\{year}_t_f.csv"
#     dataframes[year] = pd.read_csv(file_path)
#
#     # 生成无向图并检测社区
#     print(f"\n处理 {year} 年数据...")
#     G = generate_undirected_graph(create_network_from_freq(dataframes[year]))
#     print(f"网络信息：节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")
#
#     partition = detect_communities(G)
#     if partition is None:
#         print(f"{year} 年未检测到社区")
#         continue
#
#     partitions[year] = partition
#     print(f"社区检测结果已保存到 communities_{year}.csv")
#     pd.DataFrame(partition.items(), columns=['node', 'community']).to_csv(f'communities_{year}.csv', index=False)
#
# # 获取所有社区ID
# all_community_ids = set()
# for partition in partitions.values():
#     all_community_ids.update(partition.values())
# community_ids = list(all_community_ids)
# num_communities = len(community_ids)
#
# # 定义更美观的颜色方案 - 使用Plotly的默认色板
# colors = px.colors.qualitative.Plotly  # 这是一个包含10种美观颜色的列表
#
# # 如果社区数量超过颜色数量，循环使用颜色
# if num_communities > len(colors):
#     colors = colors * (num_communities // len(colors) + 1)
#
# # 创建节点数据
# entity_data = {}
#
# for year in years:
#     if year not in partitions:
#         print(f"跳过 {year} 年，因为没有检测到社区")
#         continue
#
#     data = dataframes[year]
#     partition = partitions[year]
#
#     for entity in data['word'].unique():
#         # 计算节点大小（基于词频）
#         frequency = data[data['word'] == entity]['frequency'].values[0]
#         size = min(4 + frequency * 0.01, 10)  # 调整节点大小
#
#         # 根据实际社区分配颜色
#         community_id = partition.get(entity, -1)
#         color_index = community_id % len(colors) if community_id != -1 else -1
#
#         if entity not in entity_data:
#             entity_data[entity] = {
#                 'sizes': {year: size},
#                 'communities': {year: community_id},
#                 'color_indices': {year: color_index}
#             }
#         else:
#             entity_data[entity]['sizes'][year] = size
#             entity_data[entity]['communities'][year] = community_id
#             entity_data[entity]['color_indices'][year] = color_index
#
# # 将节点数据转换为DataFrame
# entities = []
# sizes = {year: [] for year in years}
# communities = {year: [] for year in years}
# color_indices = {year: [] for year in years}
#
# for entity, data in entity_data.items():
#     entities.append(entity)
#     for year in years:
#         sizes[year].append(data['sizes'].get(year, 0))
#         communities[year].append(data['communities'].get(year, -1))
#         color_indices[year].append(data['color_indices'].get(year, -1))
#
# df = pd.DataFrame({
#     'entity': entities,
#     **{f'size_{year}': sizes[year] for year in years},
#     **{f'community_{year}': communities[year] for year in years},
#     **{f'color_index_{year}': color_indices[year] for year in years}
# })
#
# # 创建平行集图
# fig = go.Figure()
#
# # 添加平行集图 - 修正了line参数
# fig.add_trace(go.Parcats(
#     dimensions=[
#         {'label': f'{year}', 'values': df[f'community_{year}']} for year in years
#     ],
#     line={
#         'color': [colors[i] if i != -1 else '#CCCCCC' for i in df[f'color_index_{years[0]}']],
#         'shape': 'hspline'
#     },
#     labelfont={'size': 14, 'family': 'Arial', 'color': '#333333'},
#     tickfont={'size': 12, 'family': 'Arial', 'color': '#666666'},
#     arrangement='freeform'
# ))
#
# # 设置布局
# fig.update_layout(
#     title={
#         'text': '社区演变集图',
#         'y': 0.95,
#         'x': 0.5,
#         'xanchor': 'center',
#         'yanchor': 'top',
#         'font': {'size': 20, 'family': 'Arial', 'color': '#333333'}
#     },
#     width=1200,
#     height=800,
#     margin=dict(l=80, r=80, b=80, t=100),
#     paper_bgcolor='white',
#     plot_bgcolor='white'
# )
#
# # 显示图形
# print("\n开始绘制平行集图...")
# fig.show(renderer="browser")
#
# # 保存为HTML文件
# fig.write_html("community_evolution_parallel_set.html")
#
# # 保存为图片（需要安装kaleido）
# try:
#     import kaleido
#     fig.write_image("community_evolution_parallel_set.png",
#                     scale=2,
#                     width=1200,
#                     height=900,
#                     engine='kaleido')
# except ImportError:
#     print("kaleido package not installed. Please install it with: pip install kaleido")
# except Exception as e:
#     print(f"Error saving image: {e}")
#
# print("程序运行完成")



































