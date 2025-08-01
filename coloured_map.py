import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from shapely.geometry import Polygon, MultiPolygon
import os

plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取JSON文件并合并
def read_and_merge_jsons(json_files):
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
    return changjiang_gdf

# 绘制长三角地图
def plot_changjiang_delta_map(changjiang_gdf):
    fig, ax = plt.subplots(figsize=(16, 12))

    min_lon, max_lon = changjiang_gdf.bounds.minx.min() - 1, changjiang_gdf.bounds.maxx.max() + 1
    min_lat, max_lat = changjiang_gdf.bounds.miny.min() - 1, changjiang_gdf.bounds.maxy.max() + 1

    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # 设置地图背景为白色
    ax.set_facecolor('white')

    # 生成随机颜色用于渐变
    num_provinces = len(changjiang_gdf)
    cmap = plt.get_cmap('coolwarm')
    colors_list = [cmap(i / num_provinces) for i in range(num_provinces)]

    # 绘制带有频率填充的地图
    for idx, row in changjiang_gdf.iterrows():
        color = colors_list[idx]
        if isinstance(row['geometry'], Polygon):
            ax.fill(*row['geometry'].exterior.xy, facecolor=color, edgecolor='black', linewidth=0.5)
        elif isinstance(row['geometry'], MultiPolygon):
            for poly in row['geometry']:
                ax.fill(*poly.exterior.xy, facecolor=color, edgecolor='black', linewidth=0.5)

    # 添加颜色条
    norm = colors.Normalize(vmin=0, vmax=num_provinces)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
    cbar.set_label('省份编号', rotation=270, labelpad=15)

    # 设置标题
    ax.set_title('G60 地区地图', fontsize=16)

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
    plt.savefig('G60_region_map.png', dpi=300, bbox_inches='tight')
    plt.show()

# 主程序
def main():
    json_files = [
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\上海市.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\安徽省.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\浙江省.json",
        r"C:\Users\w1782\Desktop\大一下作业\数据可视化作业\dataset\newdata\output_shape\江苏省.json"
    ]

    try:
        print("读取并合并JSON文件...")
        changjiang_gdf = read_and_merge_jsons(json_files)

        print("\n生成可视化地图...")
        plot_changjiang_delta_map(changjiang_gdf)
        print("可视化完成! 结果已保存为 'G60_region_map.png'")

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


























