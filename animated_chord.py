import pandas as pd
import plotly.graph_objects as go

years = ['2122', '2223', '2324', '2425']
dataframes = {}

for year in years:
    file_path = f'C:/Users\w1782\Desktop\大一下作业\数据可视化作业\dataset/newdata/{year}_matrix_article.csv'
    dataframes[year] = pd.read_csv(file_path)

# 合并所有数据集，并添加年份列
merged_data = pd.concat([df.assign(year=year) for year, df in dataframes.items()], ignore_index=True)

# 获取所有唯一的实体
unique_entities = list(set(merged_data['Entity1']).union(set(merged_data['Entity2'])))

# 创建索引映射
entity_to_index = {entity: idx for idx, entity in enumerate(unique_entities)}

# 初始化帧列表
frames = []

for year in years:
    yearly_data = merged_data[merged_data['year'] == year]

    # 初始化源、目标和值列表
    source_indices = []
    target_indices = []
    values = []

    # 填充源、目标和值列表
    for index, row in yearly_data.iterrows():
        source_idx = entity_to_index[row['Entity1']]
        target_idx = entity_to_index[row['Entity2']]
        source_indices.append(source_idx)
        target_indices.append(target_idx)
        values.append(row['CoOccurrence'])

    # 创建当前帧的数据
    frame_data = go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=unique_entities
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(230, 230, 230, 0.1)'  # Modified line color
        )
    )

    # 添加到帧列表
    frames.append(go.Frame(data=[frame_data], name=str(year)))

# 创建初始布局
layout = go.Layout(
    title='Co-occurrence of Entities Over Four Years',
    updatemenus=[
        dict(
            type='buttons',
            showactive=False,
            buttons=[
                dict(label='Play',
                     method='animate',
                     args=[None, {'fromcurrent': True, 'transition': {'duration': 500}, 'frame': {'duration': 1000}}]),
                dict(label='Pause',
                     method='animate',
                     args=[[None], {'frame': {'duration': 0}, 'mode': 'immediate', 'transition': {'duration': 0}}])
            ]
        )
    ],
    sliders=[
        dict(
            currentvalue={'prefix': 'Year: '},
            steps=[
                dict(method='animate',
                     args=[[str(year)], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                     label=str(year)) for year in years
            ]
        )
    ]
)

# 创建初始帧数据
initial_source_indices = []
initial_target_indices = []
initial_values = []

for index, row in merged_data[merged_data['year'] == years[0]].iterrows():
    initial_source_indices.append(entity_to_index[row['Entity1']])
    initial_target_indices.append(entity_to_index[row['Entity2']])
    initial_values.append(row['CoOccurrence'])

initial_frame_data = go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=unique_entities
    ),
    link=dict(
        source=initial_source_indices,
        target=initial_target_indices,
        value=initial_values,
        color='rgba(230, 230, 230, 0.1)'  # Modified line color for initial frame
    )
)

# 创建Figure对象
fig = go.Figure(data=[initial_frame_data], layout=layout, frames=frames)

# 显示图形
fig.show(renderer='browser')

fig.write_html('sankey_diagram.html')





