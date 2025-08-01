# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.collections import LineCollection
# from matplotlib.colors import ListedColormap, to_rgba
#
# # 设置全局样式
# plt.style.use('seaborn-v0_8-darkgrid')
# sns.set_theme(style="whitegrid", context="notebook", font_scale=1.2)
# plt.rcParams['font.family'] = 'DejaVu Sans'
# plt.rcParams['axes.facecolor'] = '#f8f9fa'
#
# # 生成模拟数据
# np.random.seed(42)
# num_samples = 100
# data = {
#     'Performance': np.random.normal(70, 15, num_samples).clip(0, 100),
#     'Creativity': np.random.gamma(2, 15, num_samples).clip(0, 100),
#     'Teamwork': np.random.beta(2, 2, num_samples) * 100,
#     'Problem Solving': np.random.exponential(20, num_samples).clip(0, 100),
#     'Department': np.random.choice(['Engineering', 'Design', 'Marketing'], num_samples)
# }
# df = pd.DataFrame(data)
#
# # 标准化数据
# df_norm = df.copy()
# for col in df.columns[:-1]:
#     df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
#
# # 创建图形
# fig, ax = plt.subplots(figsize=(14, 8), facecolor='#f5f7fa')
#
# # 为每个部门分配颜色
# departments = df['Department'].unique()
# colors = sns.color_palette("husl", len(departments))
# dept_colors = dict(zip(departments, colors))
#
# # 绘制平行坐标图 - 更稳定的实现方式
# for dept in departments:
#     subset = df_norm[df_norm['Department'] == dept]
#     dept_data = subset.iloc[:, :-1].values
#
#     # 创建线段数据
#     x = np.arange(len(df.columns[:-1]))
#     y = dept_data.T  # 转置使每行代表一个观测
#
#     # 为每个观测创建线段
#     for i in range(y.shape[1]):
#         ax.plot(x, y[:, i], color=dept_colors[dept], alpha=0.5, linewidth=1.5)
#
# # 设置x轴
# ax.set_xticks(np.arange(len(df.columns[:-1])))
# ax.set_xticklabels([col.replace(' ', '\n') for col in df.columns[:-1]], fontsize=12)
# ax.set_xlim(-0.5, len(df.columns[:-1]) - 0.5)
#
# # 设置y轴
# ax.set_ylim(-0.1, 1.1)
# ax.set_yticks(np.linspace(0, 1, 5))
# ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
#
# # 添加图例
# legend_elements = [plt.Line2D([0], [0], color=dept_colors[d], lw=2, label=d)
#                    for d in departments]
# ax.legend(handles=legend_elements, title='Department',
#           loc='upper right', frameon=True, facecolor='white')
#
# # 添加标题
# plt.title('Employee Skills Assessment\nParallel Coordinates Plot',
#           fontsize=16, pad=20, fontweight='bold')
# plt.xlabel('Skills', fontsize=14, labelpad=15)
# plt.ylabel('Normalized Score', fontsize=14, labelpad=15)
#
# # 美化网格
# ax.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.5)
#
# # 添加背景标记点
# for i in range(len(df.columns[:-1])):
#     ax.scatter([i] * 5, np.linspace(0, 1, 5), s=30,
#                c='white', edgecolors='#495057', linewidths=0.5, zorder=10)
#
# plt.tight_layout()
import os
import pandas as pd
import networkx as nx
from collections import defaultdict
import plotly.express as px
import community.community_louvain as community_louvain

# 定义输出路径
OUTPUT_PATH = r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\output"


# 1. 读取并合并四个CSV文件
def read_and_combine_csvs(file_paths):
    dfs = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Add filename column to identify the year
            year = os.path.basename(file_path)[:4]
            df['year'] = year
            dfs.append(df)
        else:
            print(f"警告: 文件不存在: {file_path}")

    if not dfs:
        raise ValueError("错误: 没有可用的CSV文件")

    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


# 2. 处理地名词频数据
def process_place_frequencies(df):
    place_freq = {}

    for _, row in df.iterrows():
        word = row['word']
        freq = row['frequency']
        year = row['year']

        if word not in place_freq:
            place_freq[word] = {}
        if year not in place_freq[word]:
            place_freq[word][year] = 0
        place_freq[word][year] += freq

    result_df_list = []
    for word, yearly_freq in place_freq.items():
        yearly_data = {'word': word}
        yearly_data.update(yearly_freq)
        result_df_list.append(yearly_data)

    combined_result_df = pd.DataFrame(result_df_list)
    return combined_result_df


# 3. 社区检测
def detect_communities(G):
    """
    使用Louvain算法进行社区检测
    参数:
        G: 网络图对象
    返回:
        dict: 节点到社区ID的映射
    """
    # 需确保networkx版本>=2.0，权重参数正确传递
    partition = community_louvain.best_partition(G, weight='weight')

    # 转换为社区ID到节点列表的映射
    community_map = defaultdict(list)
    for node, community_id in partition.items():
        community_map[community_id].append(node)

    # 保存社区结果
    communities_df = pd.DataFrame([
        {'CommunityID': cid, 'Entities': ', '.join(entities)}
        for cid, entities in community_map.items()
    ])
    communities_df.to_csv(os.path.join(OUTPUT_PATH, 'communities.csv'), encoding='utf-8-sig', index=False)
    print("\n社区检测结果已保存到 communities.csv")
    return partition


# 4. 构建网络图并进行社区检测
def build_network_and_detect_communities(place_freq_df):
    G = nx.Graph()

    for _, row in place_freq_df.iterrows():
        word = row['word']
        for year in ['2122', '2223', '2324', '2425']:
            if year in row:
                G.add_node(word, year=year, frequency=row[year])
                G.nodes[word]['weight'] = row[year]

    edges = [(u, v) for u in G.nodes() for v in G.nodes() if u != v]
    G.add_edges_from(edges, weight=1)

    partition = detect_communities(G)
    return partition


# 5. 绘制平行坐标图
def plot_parallel_coordinates(place_freq_df, partition):
    # 添加社区ID到DataFrame
    place_freq_df['CommunityID'] = place_freq_df['word'].map(partition)

    # 重命名列以便于绘图
    place_freq_df.rename(columns={
        '2122': 'Year_2021_2022',
        '2223': 'Year_2022_2023',
        '2324': 'Year_2023_2024',
        '2425': 'Year_2024_2025'
    }, inplace=True)

    fig = px.parallel_coordinates(
        place_freq_df,
        dimensions=['Year_2021_2022', 'Year_2022_2023', 'Year_2023_2024', 'Year_2024_2025'],
        color='CommunityID',
        labels={'CommunityID': 'Community'},
        title='G60科创走廊长三角地区地名词频变化 (2021-2025)'
    )

    fig.show()


# 主程序
def main():
    file_paths = [
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2122_t_f.csv",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2223_t_f.csv",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2324_t_f.csv",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2425_t_f.csv"
    ]

    try:
        print("正在读取CSV文件...")
        combined_df = read_and_combine_csvs(file_paths)

        print("处理地名词频数据...")
        place_freq_df = process_place_frequencies(combined_df)
        print("\n地名词频统计:")
        print(place_freq_df.head(50))
        place_freq_df.head(50).to_csv('data.csv', encoding='utf-8-sig')
        print("\n构建网络图并进行社区检测...")
        partition = build_network_and_detect_communities(place_freq_df)

        print("\n生成平行坐标图...")
        plot_parallel_coordinates(place_freq_df, partition)
        print("可视化完成!")

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    try:
        import pandas
        import networkx as nx
        import community.community_louvain as community_louvain
        import plotly.express as px
    except ImportError:
        print("正在安装必要的库...")
        import subprocess

        subprocess.check_call(["pip", "install", "pandas", "networkx", "python-louvain", "plotly"])

    main()



