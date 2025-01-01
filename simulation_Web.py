from unzip import unzip
from sta_ltasort import sortseis
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
import numpy as np
from geopy.distance import geodesic
import shapely.errors
import time
import sys

def length(seita1, fai1, seita2, fai2): #seita:纬度 fai:经度
    distance = geodesic((seita1, fai1), (seita2, fai2)).km
    return distance

# 准备数据ing
sepointsx = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[2])
sepointsy = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[3])
sepoints = []
senames = []
log = ""
for i, j in enumerate(sepointsx):
    sepoints.append([sepointsx[i], sepointsy[i]])
for i in np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[0],dtype=np.str_):
    senames.append(i)

try:
    seislink = unzip()

    reportseisesname, reportseisestime, evdp, mag = sortseis(seislink)

    print("架空模拟启动")
    with open(r"static\log.json","w",encoding="utf-8") as f:
        log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 架空模拟准备<br>"
        json = "{\"LOG\":\"" + log + "\"}"
        f.write(json)
    with open(r"static\sc_eew.json","w",encoding="utf-8") as f:
        json = "{\"ID\": 111,\"EventID\": \"202401010704184\",\"ReportTime\": \"2024-05-25 09:54:28\",\"ReportNum\": 4,\"OriginTime\": \"2000-05-25 09:54:28\",\"HypoCenter\": \"架空模拟\",\"Latitude\": 31.517,\"Longitude\": 132.250,\"Magunitude\": 5.0, \"Depth\": 22.0, \"Delta\": 11.970983002819295}"
        f.write(json)
    benchmark = reportseisestime[0]
    for i in range(len(reportseisestime)):
        reportseisestime[i] -= benchmark
except:
    with open(r"static\log.json","w",encoding="utf-8") as f:
        log = "输入文件不合规"
        print(log)
        json = "{\"LOG\":\"" + log + "\"}"
        f.write(json)
    sys.exit()

# 计算触发的站台形成的Voronoi图
seisvoronoi = []
vor = Voronoi(sepoints)

# 前一个台站与后一个台站Voronoi区域数据
first = []
# 找到首触发台站的图
for i in vor.regions[vor.point_region[senames.index(reportseisesname[0])]]:
        first.append(vor.vertices[i].tolist())

# 打开开关
with open(r"static\switch.json","w",encoding="utf-8") as f:
    json = "{\"o\":0}"
    f.write(json)

# 上一步测定结果
prevx, prevy = 0, 0
# 发报数
n = 1
# 间隔几次测定发报
op = True
# 发报时间
reporttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

# 开始模拟计算震中
for i in range(2, len(reportseisesname)):
    with open(r"static\seis.json","w",encoding="utf-8") as f:
        json = "{\"Lat\":\"" + str(sepoints[senames.index(reportseisesname[i])][0]) + "\", \"Lon\":\"" + str(sepoints[senames.index(reportseisesname[i])][1]) + "\"}"
        f.write(json)
    # 存储测定的点与权重
    possiblepoint = []
    weight = [1]
    # 拷贝变量ing
    prev, current = [], []
    prev.append(Polygon(first))
    _sepoints = sepoints.copy()
    _senames = senames.copy()
    _reportseisesname = reportseisesname[0:i].copy()
    while len(_reportseisesname) >= 2:
        # 删去最早的台站
        _sepoints.pop(_senames.index(_reportseisesname[0]))
        _senames.pop(_senames.index(_reportseisesname[0]))
        _reportseisesname.pop(0)
        # 重新绘制新Voronoi图
        current = []
        vor = Voronoi(_sepoints)
        for i in vor.regions[vor.point_region[_senames.index(_reportseisesname[0])]]:
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
    # 发报
    if op:
        with open(r"static\log.json","w",encoding="utf-8") as f:
            log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 第{n}报: 北纬{format(resultx / totalweight, '.2f')} 东经{format(resulty / totalweight, '.2f')}<br>"
            json = "{\"LOG\":\"" + log + "\"}"
            f.write(json)
        with open(r"static\sc_eew.json","w",encoding="utf-8") as f:
            file_data = "{\"ID\": 111,\"EventID\": \"20240101070418" + str(n) + "\",\"ReportTime\": \"" + reporttime + "\",\"ReportNum\": " + str(n) + ",\"OriginTime\": \"" + reporttime + "\",\"HypoCenter\": \"架空模拟\",\"Latitude\": " + str(format(resultx / totalweight, '.2f')) + ",\"Longitude\": " + str(format(resulty / totalweight, '.2f')) + ",\"Magunitude\": " + str(mag) + ", \"Depth\": " + str(evdp) + ", \"Delta\": " + str(length(_sepoints[_senames.index(_reportseisesname[0])][0], _sepoints[_senames.index(_reportseisesname[0])][1], format(resultx / totalweight, '.2f'), format(resulty / totalweight, '.2f')) / 7.0) + "}"
            f.write(file_data)
        n += 1
        op = False
    else:
        op = True
    # 如果发报次数过多
    if n > 10:
        print("锁定")
        with open(r"static\log.json","w",encoding="utf-8") as f:
            log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 震中锁定<br>"
            json = "{\"LOG\":\"" + log + "\"}"
            f.write(json)
        break

    prevx = resultx / totalweight
    prevy = resulty / totalweight

    time.sleep(reportseisestime[i])

with open(r"static\log.json","w",encoding="utf-8") as f:
    log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 计算程序退出，可开始新模拟<br>"
    json = "{\"LOG\":\"" + log + "\"}"
    f.write(json)
    with open(r"static\switch.json","w",encoding="utf-8") as f:
        json = "{\"o\":1}"
        f.write(json)
