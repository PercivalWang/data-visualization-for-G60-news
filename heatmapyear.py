# import pandas as pd
# import seaborn as sns
# import matplotlib
# import matplotlib.pyplot as plt
#
# # 定义年份列表
# years = ['2122', '2223', '2324', '2425']
#
# # 存储每个年份的数据
# dataframes = {}
#
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# matplotlib.rcParams['axes.unicode_minus'] = False
#
# # 读取数据并存储在字典中
# for year in years:
#     file_path = rf"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\{year}_matrix_article.csv"
#     dataframes[year] = pd.read_csv(file_path)
#
# # 合并所有数据集，并添加年份列
# merged_data = pd.concat([df.assign(year=year) for year, df in dataframes.items()], ignore_index=True)
#
# # 创建一个透视表，按实体对汇总CoOccurrence值
# pivot_table = merged_data.pivot_table(index='Entity1', columns='Entity2', values='CoOccurrence', aggfunc='sum', fill_value=0)
#
# # 重新排列索引以便更好地绘制热力图
# pivot_table.sort_index(inplace=True)
# pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)
#
# # 设置图形大小
# plt.figure(figsize=(12, 10))
#
# # 绘制热力图，不显示数字
# sns.heatmap(pivot_table, annot=False, cmap='YlGnBu')
#
# # 添加标题和标签
# plt.title('Four-Year Co-occurrence Matrix Heatmap')
# plt.xlabel('Entity2')
# plt.ylabel('Entity1')
#
# # 旋转x轴标签
# plt.xticks(rotation=45, ha='right')  # 旋转45度并向右对齐
#
# # 自动调整子图参数以适应填充区
# plt.tight_layout()
#
# # 确保图形被正确渲染
# plt.draw()
#
# # 保存图形为PNG文件
# plt.savefig("four_year_cooccurrence_heatmap.png")
#
# # 显示图形
# plt.show()


import pandas as pd

# 定义年份列表
years = ['2122', '2223', '2324', '2425']

# 存储每个年份的数据
dataframes = {}

# 读取数据并存储在字典中
for year in years:
    file_path = rf"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\{year}_matrix_article.csv"
    dataframes[year] = pd.read_csv(file_path)

# 合并所有数据集，并添加年份列
merged_data = pd.concat([df.assign(year=year) for year, df in dataframes.items()], ignore_index=True)

# 创建一个透视表，按实体对汇总CoOccurrence值
pivot_table = merged_data.pivot_table(index='Entity1', columns='Entity2', values='CoOccurrence', aggfunc='sum', fill_value=0)

# 将透视表转换为长格式以便更容易筛选
long_format = pivot_table.stack().reset_index()
long_format.columns = ['Entity1', 'Entity2', 'Total_CoOccurrence']

# 提取共现值总数在6000以上的词对
filtered_pairs = long_format[long_format['Total_CoOccurrence'] > 6000]

# 打印结果
print(filtered_pairs)












