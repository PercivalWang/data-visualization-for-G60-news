import pandas as pd
import plotly.express as px
import os
# 1. 定义长三角地区的地名列表及其坐标
changjiang_delta_places = {
    '上海': [['上海', '上海市'], 121.47, 31.23],
    '江苏': [['江苏', '江苏省'], 118.78, 32.07],
    '浙江': [['浙江', '浙江省'], 120.15, 30.28],
    '安徽': [['安徽', '安徽省'], 117.28, 31.86],
    '南京': [['南京', '南京市'], 118.78, 32.07],
    '苏州': [['苏州', '苏州市'], 120.62, 31.32],
    '杭州': [['杭州', '杭州市'], 120.15, 30.28],
    '合肥': [['合肥', '合肥市'], 117.28, 31.86],
    '宁波': [['宁波', '宁波市'], 121.55, 29.88],
    '无锡': [['无锡', '无锡市'], 120.30, 31.57],
    '常州': [['常州', '常州市'], 119.95, 31.78],
    '南通': [['南通', '南通市'], 120.86, 32.01],
    '扬州': [['扬州', '扬州市'], 119.42, 32.39],
    '镇江': [['镇江', '镇江市'], 119.45, 32.20],
    '泰州': [['泰州', '泰州市'], 119.90, 32.49],
    '盐城': [['盐城', '盐城市'], 120.15, 33.35],
    '淮安': [['淮安', '淮安市'], 119.02, 33.62],
    '宿迁': [['宿迁', '宿迁市'], 118.28, 33.96],
    '徐州': [['徐州', '徐州市'], 117.18, 34.26],
    '连云港': [['连云港', '连云港市'], 119.16, 34.59],
    '温州': [['温州', '温州市'], 120.70, 28.00],
    '绍兴': [['绍兴', '绍兴市'], 120.58, 30.01],
    '湖州': [['湖州', '湖州市'], 120.09, 30.89],
    '嘉兴': [['嘉兴', '嘉兴市'], 120.76, 30.77],
    '金华': [['金华', '金华市'], 119.65, 29.08],
    '衢州': [['衢州', '衢州市'], 118.87, 28.94],
    '台州': [['台州', '台州市'], 121.42, 28.66],
    '丽水': [['丽水', '丽水市'], 119.92, 28.45],
    '舟山': [['舟山', '舟山市'], 122.20, 30.00],
    '芜湖': [['芜湖', '芜湖市'], 118.38, 31.33],
    '马鞍山': [['马鞍山', '马鞍山市'], 118.51, 31.70],
    '铜陵': [['铜陵', '铜陵市'], 117.82, 30.94],
    '安庆': [['安庆', '安庆市'], 117.07, 30.52],
    '滁州': [['滁州', '滁州市'], 118.32, 32.30],
    '池州': [['池州', '池州市'], 117.49, 30.67],
    '宣城': [['宣城', '宣城市'], 118.76, 30.95],
    '松江': [['松江', '松江区'], 121.23, 31.03],
    '虹桥': [['虹桥'], 121.38, 31.20],
    '张江': [['张江'], 121.58, 31.20],
    '临港': [['临港'], 121.88, 30.90],
    '昆山': [['昆山', '昆山市'], 120.95, 31.39],
    '嘉善': [['嘉善', '嘉善县'], 120.92, 30.84],
    '嘉兴港区': [['嘉兴港区'], 121.10, 30.60],
    '杭州湾': [['杭州湾'], 121.15, 30.30],
    '金华经开区': [['金华经开区'], 119.65, 29.08],
    '合肥高新区': [['合肥高新区'], 117.20, 31.80],
    '苏州工业园': [['苏州工业园', '苏州工业园区'], 120.70, 31.32]
}

# 2. 读取并合并四个CSV文件
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

# 3. 处理地名词频数据
def process_place_frequencies(df, place_mapping):
    place_freq = {}

    for _, row in df.iterrows():
        word = row['word']
        freq = row['frequency']
        year = row['year']

        for place_name, (variants, lon, lat) in place_mapping.items():
            if word in variants:
                if place_name not in place_freq:
                    place_freq[place_name] = {}
                if year not in place_freq[place_name]:
                    place_freq[place_name][year] = 0
                place_freq[place_name][year] += freq
                break

    result_df_list = []
    for place_name, yearly_freq in place_freq.items():
        for year, freq in yearly_freq.items():
            result_df_list.append({'place': place_name, 'year': year, 'frequency': freq})

    combined_result_df = pd.DataFrame(result_df_list)
    return combined_result_df.sort_values(by=['place', 'year'])

# 4. 绘制折线图
def plot_line_chart(place_freq_df):
    fig = px.line(place_freq_df, x='year', y='frequency', color='place',
                  title='G60 word frequncy change (2021-2025)',
                  labels={'year': '年份', 'frequency': '词频', 'place': '地名'},
                  markers=True)

    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        yaxis_title='词频',
        legend_title_text='地名'
    )

    fig.show(renderer ='browser')

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
        place_freq_df = process_place_frequencies(combined_df, changjiang_delta_places)
        print("\n地名词频统计:")
        print(place_freq_df.head())

        print("\n生成折线图...")
        plot_line_chart(place_freq_df)
        print("可视化完成!")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    try:
        import pandas
        import plotly.express as px
    except ImportError:
        print("正在安装必要的库...")
        import subprocess
        subprocess.check_call(["pip", "install", "pandas", "plotly"])

    main()





# import pandas as pd
# import plotly.express as px
#
# # 1. 读取词频表数据
# word_freq_df = pd.read_csv(r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2122_t_f.csv")
#
# # 2. 过滤高频词（例如，选择前100个高频词）
# top_n = 100
# filtered_word_freq_df = word_freq_df.nlargest(top_n, 'frequency')
#
# # 3. 准备用于Plotly的数据
# labels = []
# parents = []
# values = []
#
# # 假设所有的词频都是顶级节点
# for index, row in filtered_word_freq_df.iterrows():
#     word = row['word']
#     frequency = row['frequency']
#
#     labels.append(word)
#     parents.append('')
#     values.append(frequency)
#
# # 4. 绘制环形热力图
# fig = px.sunburst(
#     names=labels,
#     parents=parents,
#     values=values,
#     title='<b>Radial Heatmap - Top {} Word Frequencies</b>'.format(top_n),
#     branchvalues='total'
# )
#
# # 更新布局
# fig.update_layout(
#     margin=dict(t=50, l=0, r=0, b=0),
#     width=1200,
#     height=800,
#     paper_bgcolor='white',
#     plot_bgcolor='white',
#     title_x=0.5
# )
#
# # 显示图形
# fig.show(renderer='browser')
#
# # 可选：保存为HTML文件
# # fig.write_html("radial_heatmap.html")
#

#
# import pandas as pd
# import plotly.express as px
#
# # 1. 读取词频表数据
# word_freq_df = pd.read_csv(r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\2425_t_f.csv")
#
# # 2. 过滤高频词（例如，选择前50个高频词）
# top_n = 50
# filtered_word_freq_df = word_freq_df.nlargest(top_n, 'frequency')
#
# # 3. 准备用于Plotly的数据
# labels = []
# parents = []
# values = []
#
# # 假设所有的词频都是顶级节点
# for index, row in filtered_word_freq_df.iterrows():
#     word = row['word']
#     frequency = row['frequency']
#
#     labels.append(word)
#     parents.append('')
#     values.append(frequency)
#
# # 4. 绘制环形热力图
# fig = px.sunburst(
#     names=labels,
#     parents=parents,
#     values=values,
#     title='<b>Radial Heatmap - Top {} Word Frequencies of 2425</b>'.format(top_n),
#     branchvalues='total'
# )
#
# # 更新布局
# fig.update_layout(
#     margin=dict(t=50, l=0, r=0, b=0),
#     width=1200,
#     height=800,
#     paper_bgcolor='white',
#     plot_bgcolor='white',
#     title_x=0.5
# )
#
# # 显示图形
# fig.show(renderer='browser')
#
# # 可选：保存为HTML文件
# # fig.write_html("radial_heatmap.html")


























