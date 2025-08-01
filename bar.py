import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from gen_net import generate_undirected_graph, detect_communities

# 定义年份列表
years = ['2122', '2223', '2324', '2425']

# 存储每个年份的数据和分区信息
dataframes = {}
partitions = {}

# 读取数据并生成社区划分
for year in years:
    file_path = rf"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\data\{year}_matrix_article.csv"
    dataframes[year] = pd.read_csv(file_path)

    # 生成无向图并检测社区
    G = generate_undirected_graph(dataframes[year])
    partitions[year] = detect_communities(G)

# 获取所有社区ID
all_community_ids = set()
for partition in partitions.values():
    all_community_ids.update(partition.values())
community_ids = list(all_community_ids)
num_communities = len(community_ids)

# 确保至少有3个社区，如果不足则补充虚拟社区
if num_communities < 3:
    for i in range(3 - num_communities):
        community_ids.append(max(community_ids) + 1)

# 定义三种颜色
colors = ['#FFFF99', '#ADD8E6', '#90EE90']  # 浅黄, 浅蓝, 浅绿

# 创建节点数据
nodes = []
for year in years:
    data = dataframes[year]
    partition = partitions[year]

    for entity in data['Entity1'].unique():
        # 计算节点大小（基于共现次数）
        total_cooccurrence = data[(data['Entity1'] == entity) | (data['Entity2'] == entity)]['CoOccurrence'].sum()
        size = min(4 + total_cooccurrence * 0.4, 10)  # 调整节点大小

        # 根据实际社区分配颜色
        community_color = partition.get(entity, -1)
        color = colors[community_color % 3]  # 使用定义的颜色列表

        nodes.append({
            'entity': entity,
            'year': year,
            'size': size,
            'color': color,
            'community': community_color
        })

# 创建平行条图
fig = go.Figure()

# 添加条形图
for community_id, color in zip(range(len(colors)), colors):
    community_nodes = [node for node in nodes if node['community'] == community_id]
    entities = [node['entity'] for node in community_nodes]
    sizes = [node['size'] for node in community_nodes]
    years = [node['year'] for node in community_nodes]

    fig.add_trace(go.Bar(
        x=years,
        y=sizes,
        name=f'Community {community_id}',
        marker=dict(color=color),
        customdata=entities,
        hovertemplate='Year: %{x}<br>Entity: %{customdata}<br>Size: %{y}'
    ))

# 设置布局
fig.update_layout(
    title='平行条图：基于社区检测的关系网络',
    xaxis_title='年份',
    yaxis_title='共现次数',
    barmode='group',
    width=1000,
    height=800,
    margin=dict(l=50, r=50, b=50, t=100),
    paper_bgcolor='white'
)

# 显示图形
fig.show(renderer="browser")

# 保存为HTML文件
# fig.write_html("parallel_bar_chart.html")

# 保存为图片（需要安装kaleido）
fig.write_image("parallel_bar_chart.png", scale=2, width=1200, height=900)



