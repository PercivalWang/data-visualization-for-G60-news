import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import os
from gen_net import generate_undirected_graph, detect_communities


def calculate_centralities(G):
    degree_centrality = nx.degree_centrality(G)
    weighted_degree = {node: sum(d["weight"] for _, d in G[node].items()) for node in G.nodes}

    # 计算加权度中心性
    weighted_degree_centrality = nx.betweenness_centrality(G, weight='weight')

    # 计算接近中心性
    closeness_centrality = nx.closeness_centrality(G)

    # 计算特征向量中心性
    eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)

    # 保存到 DataFrame
    df_metrics = pd.DataFrame({
        "Entity": degree_centrality.keys(),
        "DegreeCentrality": degree_centrality.values(),  # 节点连接数
        "WeightedDegree": weighted_degree.values(),  # 加权度中心性
        "BetweennessCentrality": weighted_degree_centrality.values(),  # 中介中心性
        "ClosenessCentrality": closeness_centrality.values(),  # 接近中心性
        "EigenvectorCentrality": eigenvector_centrality.values()  # 特征向量中心性
    })

    return df_metrics
# 定义年份列表
years = ['2122', '2223', '2324', '2425']

# 存储每个年份的数据
dataframes = {}

# 定义输出路径
OUTPUT_PATH = r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata"

# 读取数据并存储在字典中
for year in years:
    file_path = rf"{OUTPUT_PATH}\{year}_matrix_article.csv"
    dataframes[year] = pd.read_csv(file_path)

# 存储每个年份的中心性指标
centralities_by_year = {}

# 处理每个年份的数据
for year in years:
    print(f"\n处理 {year} 年数据...")
    df_matrix = dataframes[year]
    G = generate_undirected_graph(df_matrix)
    centralities_by_year[year] = calculate_centralities(G)
    communities_df, _ = detect_communities(G)
    communities_df.to_csv(f'{OUTPUT_PATH}\\communities_{year}.csv', encoding='utf-8-sig', index=False)
    print("\n社区检测结果已保存到 communities_{year}.csv")

# 合并所有年份的中心性指标
merged_centralities = pd.concat(centralities_by_year.values(), keys=years).reset_index(level=1, drop=True).reset_index().rename(columns={'index': 'Year'})

# 读取词语分类文件
category_file = rf"{OUTPUT_PATH}\entity_dict.csv"
entity_categories = pd.read_csv(category_file)

# 合并中心性指标和类别信息
merged_data = pd.merge(merged_centralities, entity_categories, on='Entity', how='left')

# 提取主要中心性指标
main_centralities = merged_data[['Year', 'Entity', 'Category', 'DegreeCentrality', 'WeightedDegree', 'BetweennessCentrality', 'ClosenessCentrality', 'EigenvectorCentrality']]

# 获取每个年份每个类别的前5个实体
top_entities_by_year_category = main_centralities.groupby(['Year', 'Category']).apply(lambda x: x.nlargest(5, 'WeightedDegree')).reset_index(drop=True)

# 绘制条形图
plt.figure(figsize=(16, 12))

categories = ['产业', '资本', '技术']
centrality_metric = 'WeightedDegree'

for i, category in enumerate(categories):
    plt.subplot(2, 2, i + 1)
    category_data = top_entities_by_year_category[top_entities_by_year_category['Category'] == category]
    sns.barplot(x='Year', y=centrality_metric, hue='Entity', data=category_data, palette='viridis')
    plt.title(f'Top 5 Entities by Weighted Degree Centrality - {category}')
    plt.xlabel('Year')
    plt.ylabel('Weighted Degree Centrality')
    plt.xticks(rotation=45)
    plt.legend(title='Entity', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.suptitle('Top 5 Entities by Weighted Degree Centrality Across Categories Over Four Years', fontsize=16)
plt.show()

# 保存图形为PNG文件
plt.savefig("top_entities_weighted_degree_centrality.png")



