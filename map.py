import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from shapely.geometry import Point, Polygon
import os
from shapely.validation import explain_validity

plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

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

    for place_name in place_mapping:
        place_freq[place_name] = {
            'frequency': 0,
            'longitude': place_mapping[place_name][1],
            'latitude': place_mapping[place_name][2]
        }

    for _, row in df.iterrows():
        word = row['word']
        freq = row['frequency']

        for place_name, (variants, lon, lat) in place_mapping.items():
            if word in variants:
                place_freq[place_name]['frequency'] += freq
                break

    result_df = pd.DataFrame.from_dict(place_freq, orient='index')
    result_df = result_df[result_df['frequency'] > 0]
    result_df.reset_index(inplace=True)
    result_df.rename(columns={'index': 'place'}, inplace=True)

    return result_df.sort_values('frequency', ascending=False)


# 4. 绘制长三角地图并标注地名词频
def plot_changjiang_delta_map(place_freq_df):
    fig, ax = plt.subplots(figsize=(16, 12))

    geometry = [Point(xy) for xy in zip(place_freq_df['longitude'], place_freq_df['latitude'])]
    gdf = gpd.GeoDataFrame(place_freq_df, geometry=geometry, crs="EPSG:4326")

    min_lon, max_lon = gdf['longitude'].min() - 1, gdf['longitude'].max() + 1
    min_lat, max_lat = gdf['latitude'].min() - 1, gdf['latitude'].max() + 1

    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # 读取JSON文件
    json_files = [
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\上海市.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\安徽省.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\浙江省.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\江苏省.json"
    ]

    provinces_gdfs = []

    for json_file in json_files:
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"文件不存在: {json_file}")

        province_gdf = gpd.read_file(json_file)

        # 删除不受支持的字段
        unsupported_fields = ['center', 'centroid', 'acroutes']
        for field in unsupported_fields:
            if field in province_gdf.columns:
                del province_gdf[field]

        # 验证和修复几何对象
        valid_geoms = province_gdf.geometry.apply(lambda geom: geom if geom.is_valid else geom.buffer(0))
        province_gdf['geometry'] = valid_geoms

        provinces_gdfs.append(province_gdf)

    changjiang_gdf = pd.concat(provinces_gdfs).reset_index(drop=True)

    # 裁剪到指定范围
    bbox = Polygon([(min_lon, min_lat), (max_lon, min_lat), (max_lon, max_lat), (min_lon, max_lat)])
    changjiang_gdf = changjiang_gdf.clip(bbox)

    # 设置地图背景为白色
    ax.set_facecolor('white')

    changjiang_gdf.plot(ax=ax, edgecolor='black', facecolor='white', linewidth=1)

    # 准备颜色映射
    norm = colors.Normalize(vmin=place_freq_df['frequency'].min(),
                            vmax=place_freq_df['frequency'].max())
    cmap = plt.get_cmap('coolwarm')  # 使用更深的颜色映射

    # 在地图上标注地名词频
    for _, row in gdf.iterrows():
        color = cmap(norm(row['frequency']))
        ax.text(row['longitude'], row['latitude'],
                row['place'],
                fontsize=10, ha='center', va='center',
                color=color, fontweight='bold')

    # 添加颜色条
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
    cbar.set_label('词频', rotation=270, labelpad=15)

    # 设置标题
    ax.set_title('G60 Word Frequency Map (2021-2025)', fontsize=16)

    # 添加比例尺和指北针
    ax.annotate('N', xy=(0.9, 0.95), xycoords='axes fraction',
                fontsize=12, ha='center', va='center')
    ax.plot([0.85, 0.85], [0.9, 0.85], 'k-', lw=1, transform=ax.transAxes)
    ax.plot([0.8, 0.9], [0.85, 0.85], 'k-', lw=1, transform=ax.transAxes)
    ax.text(0.85, 0.83, '100km', ha='center', va='top', transform=ax.transAxes)

    # 添加图例说明
    ax.text(0.02, 0.02, '注: 地图边界为简化示意',
            transform=ax.transAxes, fontsize=10, color='gray')

    # 移除坐标轴
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig('G60_word_frequency_map.png', dpi=300, bbox_inches='tight')
    plt.show()


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
        print("\n地名词频统计(前20名):")
        print(place_freq_df.head(20))

        print("\n生成可视化地图...")
        plot_changjiang_delta_map(place_freq_df)
        print("可视化完成! 结果已保存为 'G60_word_frequency_map.png'")

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    try:
        import geopandas
    except ImportError:
        print("正在安装必要的库...")
        import subprocess

        subprocess.check_call(["pip", "install", "geopandas", "contextily", "shapely"])

    main()



# 4. 绘制长三角地图并标注地名词频
# def plot_changjiang_delta_map(place_freq_df):
#     # 创建图形时禁用自动宽高比
#     fig, ax = plt.subplots(figsize=(14, 12))
#     ax.set_aspect('auto')  # 修复点1
#
#     # 生成 GeoDataFrame
#     geometry = [Point(xy) for xy in zip(place_freq_df['longitude'], place_freq_df['latitude'])]
#     gdf = gpd.GeoDataFrame(place_freq_df, geometry=geometry, crs="EPSG:4326")
#
#     # 固定坐标范围（避免自动计算）
#     min_lon, max_lon = 115, 123  # 修复点2
#     min_lat, max_lat = 27, 35
#     ax.set_xlim(min_lon, max_lon)
#     ax.set_ylim(min_lat, max_lat)
#
#     # 加载地图数据（确保路径正确）
#     naturalearth_filepath = r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\ne_110m_admin_1_states_provinces.shp"
#     world = gpd.read_file(naturalearth_filepath)
#     china = world[world.iso_a2 == 'CN']
#
#     # 提取长三角地区（注意名称匹配）
#     changjiang_provinces = ['Shanghai', 'Jiangsu', 'Zhejiang', 'Anhui']  # 或中文名
#     changjiang_gdf = china[china.name.isin(changjiang_provinces)]
#
#     # 裁剪并绘制
#     bbox = Polygon([(min_lon, min_lat), (max_lon, min_lat), (max_lon, max_lat), (min_lon, max_lat)])
#     changjiang_gdf = changjiang_gdf.clip(bbox)
#     changjiang_gdf.plot(ax=ax, edgecolor='black', facecolor='lightgray', linewidth=1)
#
#     # 标注省份名称
#     for _, row in changjiang_gdf.iterrows():
#         centroid = row['geometry'].centroid
#         ax.text(centroid.x, centroid.y, row['name'],
#                 fontsize=12, ha='center', va='center',
#                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
#
#     # 绘制长江和钱塘江（简化版）
#     yangtze_river = [(116.0, 31.0), (117.0, 31.5), (118.0, 32.0),
#                      (119.0, 32.0), (120.0, 31.8), (121.5, 31.5)]
#     qiantang_river = [(118.5, 29.5), (120.0, 30.0), (121.5, 30.3)]
#
#     ax.plot(*zip(*yangtze_river), color='blue', linewidth=1, linestyle='--', alpha=0.5)
#     ax.plot(*zip(*qiantang_river), color='blue', linewidth=1, linestyle='--', alpha=0.5)
#
#     # 准备颜色映射
#     norm = colors.Normalize(vmin=place_freq_df['frequency'].min(),
#                             vmax=place_freq_df['frequency'].max())
#     cmap = plt.get_cmap('YlOrRd')  # 使用黄色到红色的渐变色
#
#     # 绘制点
#     sc = gdf.plot(ax=ax, marker='o',
#                   markersize=gdf['frequency'] / 100 + 10,  # 根据词频调整点大小
#                   color=[cmap(norm(freq)) for freq in gdf['frequency']],
#                   alpha=0.8, edgecolor='white')
#
#     # 添加标注
#     for _, row in gdf.iterrows():
#         ax.text(row['longitude'], row['latitude'],
#                 f"{row['place']}\n{int(row['frequency'])}",
#                 fontsize=8, ha='center', va='bottom',
#                 bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'))
#
#     # 添加颜色条
#     sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
#     cbar.set_label('词频', rotation=270, labelpad=15)
#
#     # 设置标题
#     ax.set_title('G60科创走廊长三角地区地名词频分布 (2021-2025)', fontsize=16)
#
#     # 添加比例尺和指北针
#     ax.annotate('N', xy=(0.9, 0.95), xycoords='axes fraction',
#                 fontsize=12, ha='center', va='center')
#     ax.plot([0.85, 0.85], [0.9, 0.85], 'k-', lw=1, transform=ax.transAxes)
#     ax.plot([0.8, 0.9], [0.85, 0.85], 'k-', lw=1, transform=ax.transAxes)
#     ax.text(0.85, 0.83, '100km', ha='center', va='top', transform=ax.transAxes)
#
#     # 添加图例说明
#     ax.text(0.02, 0.02, '注: 地图边界为简化示意',
#             transform=ax.transAxes, fontsize=10, color='gray')
#
#     # 移除坐标轴
#     ax.set_axis_off()
#
#     plt.tight_layout()
#     plt.savefig('G60长三角地名词频分布.png', dpi=300, bbox_inches='tight')
#     plt.show()



























