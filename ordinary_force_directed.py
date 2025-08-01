import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from community import community_louvain
import numpy as np

# 1. 导入数据
df = pd.read_csv(r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2122_matrix_article.csv")

# 2. 构建网络
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(row['Entity1'], row['Entity2'], weight=row['CoOccurrence'])

# 3. 计算社区（Louvain算法）
partition = community_louvain.best_partition(G)
communities = list(set(partition.values()))

# 4. 准备绘图数据
pos = nx.spring_layout(G, k=0.5, iterations=50)  # 使用二维布局

node_x = [pos[node][0] for node in G.nodes()]
node_y = [pos[node][1] for node in G.nodes()]

degrees = dict(nx.degree(G))
node_sizes = [np.sqrt(degrees[node]) * 10 for node in G.nodes()]
colors = [partition[node] for node in G.nodes()]

# 5. 创建散点图（节点）
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=list(G.nodes()),
    textposition="top center",
    hoverinfo='text',
    marker=dict(
        size=node_sizes,
        color=colors,
        colorscale='Viridis',
        line=dict(width=0.5, color='gray')
    )
)

# 6. 绘制边
edge_x, edge_y = [], []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=0.5, color='#888')  # 去掉 opacity 属性
)

# 7. 组合图形
fig = go.Figure(data=[edge_trace, node_trace])

# 8. 设置布局
fig.update_layout(
    title='G60实体交互式网络',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    showlegend=False,
    hovermode='closest',
    margin=dict(b=0, l=0, r=0, t=30)
)

fig.show(renderer="browser")