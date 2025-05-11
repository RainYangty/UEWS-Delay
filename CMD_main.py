import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
from _unzip import unzip
from sta_ltasort import sortseis
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from seis import updated_one_seis
"""
--- 输入数据  ---
sepoints: 所有地震台站的坐标列表 (例如 [(x1, y1), (x2, y2), ...])
senames: 与 sepoints 对应的台站名称列表 (例如 ['StationA', 'StationB', ...])
reportseisesname: 按报告探测到地震事件的顺序排列的台站名称列表
"""
sepoints    = []
_senames    = []
senames     = []
stationdata = []
seismograph = []
# 获取当前工作目录路径
current_path = os.getcwd()
print("处理台站数据")
with open(current_path + "\\sitepub_all_en.csv", "rb") as stationdata:
    seismograph = np.loadtxt(stationdata, delimiter=",", usecols=[7], dtype=np.str_)
    stationdata.seek(0)
    sepointsx = np.loadtxt(stationdata, delimiter=",", usecols=[2])
    # 将文件指针移回开头
    stationdata.seek(0)
    sepointsy = np.loadtxt(stationdata, delimiter=",", usecols=[3])
    stationdata.seek(0)
    for i in np.loadtxt(stationdata, delimiter=",", usecols=[0], dtype=np.str_):
        _senames.append(i)
num = 0 # 弃用台站数
for i, j in enumerate(sepointsx):
    # 除去弃用站点
    if not seismograph[i] == "---":
        sepoints.append([sepointsx[i], sepointsy[i]])
        senames.append(_senames[i])
    else:
        # print(_senames[i])
        num += 1
print(f"{num}个台站已弃用")

seislink = unzip()

reportseisesname, _, _, _ = sortseis(seislink)

no_data = 0
with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            refresh_per_second = 100,
) as progress:
    task = progress.add_task("核对台站数据", total = len(reportseisesname))
    # print("核对台站数据")
    for i in reportseisesname:
        try:
            senames.index(i)
        except:
            pointx, pointy = updated_one_seis(i, seislink)
            no_data += 1
            if not pointx == None:
                sepoints.append([round(pointx, 4), round(pointy, 4)])
                senames.append(i)
        progress.update(task, advance = 1)

if no_data:
    print(f"{no_data}个台站表中无数据, 请及时更新台站表格数据")

# 存储台站点位便于绘图
seispoints = []
for i in reportseisesname:
    seispoints.append(sepoints[senames.index(i)])   

""" 
--- 步骤 1: 初始化 Voronoi 图和初始区域 ---
"""
# 计算最初触发的台站形成的 Voronoi 图
# 这将平面划分为 Voronoi 区域，每个区域包含离某个特定台站最近的所有点
vor = Voronoi(sepoints)
# 初始化列表，用于存储潜在震中区域的历史 (以多边形表示)
# 以及当前台站 Voronoi 区域的顶点
area_history, current_region_vertices = [], []

# 找到 *第一个* 触发台站对应的 Voronoi 区域
with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn()
) as progress:
    task = progress.add_task("进行震中计算", total = len(reportseisesname) - 1)
    # 在原始台站名称列表中找到第一个触发台站的索引
    first_station_index = senames.index(reportseisesname[0])
    reportseisesname.pop(0)
    # 获取与该台站对应的 Voronoi 区域的索引
    first_region_index = vor.point_region[first_station_index]
    # 获取该区域的顶点索引列表
    first_region_vertex_indices = vor.regions[first_region_index]
    # 获取该区域每个顶点的坐标并存储
    for i in first_region_vertex_indices:
        current_region_vertices.append(vor.vertices[i].tolist())
    # 从顶点创建第一个台站 Voronoi 区域的 Polygon 对象
    # 这个多边形代表了震中最初的可能区域
    initial_area = Polygon(current_region_vertices)
    area_history.append(initial_area)
    # 存储确定的潜在震中点 (交集区域的质心)
    # 以及它们对应的权重。
    possible_region = [initial_area]
    weights = [1]    # 第一个区域质心的初始权重
    progress.update(task, advance = 1)

    """
    --- 步骤 2: 遍历触发台站以细化区域 ---
    """
    # 从第二个触发台站开始处理。
    # 循环继续，只要触发顺序列表中还剩下至少两个台站。
    # 第一个台站已用于初始化，循环处理后续的台站
    while len(reportseisesname) >= 2:
        # 从列表中移除最早处理的台站的信息
        # 从 *原始* 台站列表中弹出，基于 *当前* 触发顺序中的第一个台站
        sepoints.pop(senames.index(reportseisesname[0]))
        senames.pop(senames.index(reportseisesname[0]))
        reportseisesname.pop(0)

        # 获取触发顺序中的下一个台站名称。
        next_station_name = reportseisesname[0]
        
        # 基于剩余的台站重新计算 Voronoi 图
        current_region_vertices = []
        vor                     = Voronoi(sepoints)

        # 在 *新的* 图中找到下一个触发台站对应的 Voronoi 区域
        next_station_index          = senames.index(next_station_name)
        next_region_index           = vor.point_region[next_station_index]
        next_region_vertex_indices  = vor.regions[next_region_index]
        for i in next_region_vertex_indices:
            current_region_vertices.append(vor.vertices[i].tolist())

        # 为当前台站的 Voronoi 区域创建 Polygon 对象。
        current_station_voronoi_area = Polygon(current_region_vertices)

        # 计算之前的累积区域与当前台站区域的交集。
        # 若均无交集则另辟蹊径，再建新的累计区域
        try:
            intered = False
            for region_index, region in enumerate(possible_region):
                intersection = region.intersection(current_station_voronoi_area)
                if not intersection.is_empty:
                    intered = True
                    weights[region_index] += 1
            if not intered:
                # 新建累计区域
                possible_region.append(current_station_voronoi_area)
                # 为这个新的潜在区域序列开始一个新的权重，初始值为 1。
                weights.append(1)
        except:
            print("请立即更新台站数据表，计算程序退出")
            break
        # 更新进度
        progress.update(task, advance = 1)

"""
--- 步骤 3: 计算加权平均结果 ---
"""
resultx      = 0
resulty      = 0
totalweights = 0
# 遍历保存的候选点及其对应的权重。
for i in range(len(possible_region)):
    point    = possible_region[i].centroid
    weight   = weights[i]
    # 去除只由单一台站确定的区域
    if weight > 1:
        resultx += point.x * weight
        resulty += point.y * weight
        totalweights += weight

print(f"({format(resultx / totalweights, '.2f')}, {format(resulty / totalweights, '.2f')})")

# --- 步骤 4: 将结果以图的形式表示 ---
# 设置图表大小，确定画布
plt.figure(figsize=(10, 10))

# 建立颜色列表，及建立标签类别列表
colors = ['black', 'red']  
labels = ['seis', 'Voronoi']
seispoints = np.array(seispoints)
# 绘图
plt.scatter(seispoints[:, 0],  # 横坐标
            seispoints[:, 1],  # 纵坐标
            marker='^', # 标记: 向上三角形
            c=colors[0],  # 颜色
            label=labels[0])  # 标签
    
plt.scatter(resultx / totalweights,  # 横坐标
            resulty / totalweights,  # 纵坐标
            marker='+', # 标记: 加号
            c=colors[1],  # 颜色
            label=labels[1])  # 标签

plt.title("epicenter")

# 展示图形
plt.legend()  # 显示图例

plt.show()  # 显示图片