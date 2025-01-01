from unzip import unzip
from sta_ltasort import sortseis
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
import numpy as np
from geopy.distance import geodesic
import shapely.errors

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

# test
""" reportseisesname = ["IBRH20",
"CHB005",
"IBR018",
"CHB004",
"CHB010",
"IBRH08",
"CHBH06",
"IBR013",
"CHBH19",
"CHB011",
"IBRH07",
"IBR017",
"CHBH13",
"CHB006",
"IBR007",
"CHB012",
"CHB007",
"IBR012",
"IBR014",
"IBR006",
"CHBH10",
"IBR016",
"IBR011",
"CHB013",
] """

# 对精度影响不大
""" for i in reportseisesname:
    sepoints.append(_sepoints[_senames.index(i)])
    senames.append(_senames[_senames.index(i)]) """

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
# 存储测定的点与权重
possiblepoint = []
weight = [1]

# 开始计算震中
while len(reportseisesname) >= 2:
    # 删去最早的台站
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

    # 如果没有交集惹，那就保存该结果与权重
    if prev[-1].centroid.is_empty:
        possiblepoint.append(prev[-2].centroid)
        prev[-1] = Polygon(current)
        weight.append(1)
        continue
    # 有交集权重+1
    weight[-1] += 1

# 加权计算结果
resultx = 0
resulty = 0
totalweight = 0
for i in range(len(possiblepoint)):
    resultx += possiblepoint[i].x * weight[i]
    resulty += possiblepoint[i].y * weight[i]
    totalweight += weight[i]

print(format(resultx / totalweight, '.2f'), format(resulty / totalweight, '.2f'))
