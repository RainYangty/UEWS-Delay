from unzip import unzip
from sta_ltasort import sortseis
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
import numpy as np
from geopy.distance import geodesic

def find_deviation(seispoints, possiblecenter):
    """
    查找与标准速度比较最不符合的台站索引

    参数:
    seispoints: 台站坐标
    possiblecenter: 估计可能的震中

    返回:
    int: 找到的台站索引值
    """

    deviation_index = 0
    time = []
    for seis in seispoints:
        distance = geodesic((seis[0], seis[1]), (possiblecenter.x, possiblecenter.y)).km
        Ptime = distance / 7.0
        time.append(Ptime)
        diff = np.diff(time)
        # 因为删除该数组按照理论震中距排序，故判断到时是否单增即可
        for i in range(len(diff) - 1):
            if diff[i] < 0:
                deviation_index = i
    return deviation_index
    

# 准备数据ing
sepointsx = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[2])
sepointsy = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[3])
sepoints = []
senames = []
for i, j in enumerate(sepointsx):
    sepoints.append([sepointsx[i], sepointsy[i]])
for i in np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[0],dtype=np.str_):
    senames.append(i)

seislink = unzip()

reportseisesname, _, _, _ = sortseis(seislink)

# 计算触发的站台形成的Voronoi图
seisvoronoi = []
vor = Voronoi(sepoints)
for i in vor.regions[vor.point_region[senames.index(reportseisesname[0])]]:
    seisvoronoi.append(vor.vertices[i].tolist())
# 变为多边形对象
seisvoronoi = Polygon(seisvoronoi)

# 前一个台站与后一个台站Voronoi区域数据
prev, current, first = [], [], []
# 找到首触发台站的图
for i in vor.regions[vor.point_region[senames.index(reportseisesname[0])]]:
        first.append(vor.vertices[i].tolist())
prev.append(Polygon(first))
#存储删去的台站名称、坐标、索引方便回溯
delseisname = []
delseispoints = []
delseisindex = []

# 开始计算震中
while len(reportseisesname) >= 2:
    # 删去最早的台站
    delseisname.append(reportseisesname[0])
    delseispoints.append(sepoints[senames.index(reportseisesname[0])])
    delseisindex.append(senames.index(reportseisesname[0]))
    sepoints.pop(senames.index(reportseisesname[0]))
    senames.pop(senames.index(reportseisesname[0]))
    reportseisesname.pop(0)
    # 重新绘制新Voronoi图
    current = []
    vor = Voronoi(sepoints)
    for i in vor.regions[vor.point_region[senames.index(reportseisesname[0])]]:
        current.append(vor.vertices[i].tolist())

    # 下一个触发台站所在的Voronoi区域与前计算结果区域取交集
    prev.append(prev[-1].intersection(Polygon(current)))

    # 如果没有交集惹，那就代表计算P波初始相位误差较大，对比删去误差最大者，并回溯重新计算
    if prev[-1].centroid.is_empty:
        deviation_index = find_deviation(delseispoints, prev[-2].centroid)
        delseispoints.pop(deviation_index)
        delseisname.pop(deviation_index)
        delseisindex.pop(deviation_index)
        # 恢复至该步骤之前状态(优化?)
        prev_len = len(prev)
        prev.pop()
        for i in range(0, prev_len - deviation_index - 2):
            sepoints.insert(delseisindex[-1], delseispoints[-1])
            senames.insert(delseisindex[-1], delseisname[-1])
            prev.pop(), delseisindex.pop(), delseispoints.pop(), delseisname.pop()

print(prev[-1].centroid)