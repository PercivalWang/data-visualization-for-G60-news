import pandas as pd
import networkx as nx
import community as community_louvain
from collections import defaultdict
import holoviews as hv
from holoviews import opts, dim
import matplotlib.pyplot as plt
import os

# 启用bokeh后端
hv.extension('bokeh')


# 1. 数据处理和社区检测函数
def process_data(file_path):
    df = pd.read_csv(file_path)

    # 创建无向图
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["Entity1"], row["Entity2"], weight=row["CoOccurrence"])

    # 社区检测 (Louvain算法)
    partition = community_louvain.best_partition(G, weight='weight')

    # 将社区信息添加到原始数据
    df['Community1'] = df['Entity1'].map(partition)
    df['Community2'] = df['Entity2'].map(partition)

    return df, G, partition


# 2. 使用holoviews绘制弦图
def plot_chord_diagram(df, title):
    # 准备数据：源节点、目标节点、权重
    sources = df['Entity1'].tolist()
    targets = df['Entity2'].tolist()
    values = df['CoOccurrence'].tolist()

    # 创建Chord对象
    chord = hv.Chord((sources, targets, values))

    # 设置可视化参数
    chord.opts(
        opts.Chord(
            cmap='Category20',
            edge_cmap='Category20',
            edge_color=dim('source').str(),
            labels='index',
            node_color=dim('index').str(),
            title=title,
            width=800,
            height=800
        )
    )

    return chord


# 3. 分析社区变化趋势（保持不变）
def analyze_community_trends(years):
    community_data = []

    for year in years:
        file_path = f"C:/Users/w1782/Desktop/大一下作业/数据可视化作业/dataset/newdata/{year}_matrix_article.csv"
        df, G, partition = process_data(file_path)

        # 统计社区大小
        comm_counts = defaultdict(int)
        for node, comm in partition.items():
            comm_counts[comm] += 1

        # 按社区大小排序并选择前3
        sorted_comms = sorted(comm_counts.items(), key=lambda x: -x[1])[:3]
        community_data.append({f"Community {k}": v for k, v in sorted_comms})

    # 转换为DataFrame
    df_trend = pd.DataFrame(community_data, index=[f"20{y[:2]}-20{y[2:]}" for y in years])
    df_trend = df_trend.fillna(0)

    # 绘制趋势图
    fig = df_trend.plot(
        kind='line',
        marker='o',
        figsize=(10, 6),
        title="Community Size Trends (Top 3 Communities)"
    )
    plt.xlabel("Year")
    plt.ylabel("Number of Entities")
    plt.grid(True)

    return fig, df_trend


# 主程序
if __name__ == "__main__":
    # 设置文件路径
    input_file = r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2122_matrix_article.csv"

    # 1. 处理数据并绘制弦图
    df, G, partition = process_data(input_file)
    chord = plot_chord_diagram(df, "Entity Co-occurrence Network (2021-2022)")
    hv.save(chord, 'chord_diagram.html')  # 保存为HTML文件
    display(chord)  # 在Jupyter中显示

    # 2. 分析四年社区变化趋势
    years = ['2122', '2223', '2324', '2425']
    trend_fig, df_trend = analyze_community_trends(years)
    plt.show()

    print("\nCommunity size changes over years:")
    print(df_trend)