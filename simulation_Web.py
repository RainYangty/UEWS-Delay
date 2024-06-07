from unzip import unzip
from sta_ltasort import sortseis
import time
from threading import Thread
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
import numpy as np
import shapely
from geopy.distance import geodesic
import sys

"""
这里写得有点小乱，我错惹......
"""

log = ""
# 初始化
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

triggernum = 0

sepointsx = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[2])
sepointsy = np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[3])
sepoints = []
senames = []
for i, j in enumerate(sepointsx):
    sepoints.append([sepointsx[i], sepointsy[i]])
for i in np.loadtxt(open("sitepub_all_en.csv","rb"),delimiter=",",usecols=[0],dtype=np.str_):
    senames.append(i)

seisvoronoi = []
# 计算站台的泰森多边形
vor = Voronoi(sepoints)
for i in vor.regions[vor.point_region[senames.index(reportseisesname[0])]]:
    seisvoronoi.append(vor.vertices[i].tolist())
seisvoronoi = Polygon(seisvoronoi)
center = []
use = []
_open = False
ok = False
seistrynum = 0
reportnum = 0
prevcenter = []
prevuse = []
n = 1
lock = 0
reporttime = 0
error = False

with open(r"static\switch.json","w",encoding="utf-8") as f:
    json = "{\"o\":0}"
    f.write(json)

'''
利用递归去尝试排除触发顺序有误的台站，进行震中计算
'''
def hypocenter(prev, prev_center, reportseis, allseis, allseisname, ii, useseis):
    global ok
    global center, use, seistrynum
    try:
        useseis.append(allseisname[allseisname.index(reportseis[0])])
        allseis.pop(allseisname.index(reportseis[0]))
        allseisname.pop(allseisname.index(reportseis[0]))
        reportseis.pop(0)
        current = []
        # 计算去掉触发测站后的泰森多边形
        vor = Voronoi(allseis)
        for i in vor.regions[vor.point_region[allseisname.index(reportseis[0])]]:
            current.append(vor.vertices[i].tolist())
    except IndexError:
        return
    try:
        prev = prev.intersection(Polygon(current))
    except shapely.errors.GEOSException:
        return
    if prev.centroid.is_empty:
        return
    if prev_center != [] and prev.centroid != []:
        if ii > seistrynum:
            center = prev.centroid
            seistrynum = ii
            center = prev.centroid
            use = useseis
        if format(prev_center.x, '.3f') == format(prev.centroid.x, '.3f') and format(prev_center.y, '.3f') == format(prev.centroid.y, '.3f'):
            # print("锁定")
            return
    a = prev.centroid
    for i in range(len(reportseis)):
        hypocenter(prev, a, reportseis.copy(), allseis.copy(), allseisname.copy(), ii+1, useseis.copy())
        if ok:
            return
        allseis.pop(allseisname.index(reportseis[0]))
        allseisname.pop(allseisname.index(reportseis[0]))
        reportseis.pop(0)
        #print(reportseisesname)
        #print(1)

'''
计算地球上两点间的面距离,用于修正地震开始时间
'''
def length(seita1, fai1, seita2, fai2): #seita:纬度 fai:经度
    distance = geodesic((seita1, fai1), (seita2, fai2)).km
    return distance

def cal():
    global ok, sepoints, senames, evdp, mag, log, error
    global center, use, seistrynum, prevcenter, prevuse, reportnum, n, reporttime, triggernum
    while triggernum <= 10: #len(reportseisesname):
        if triggernum >= 3:
            #print("Finding")
            reportseisesname_copy = reportseisesname[:triggernum - 1].copy()
            sepoints_copy = sepoints.copy()
            senames_copy = senames.copy()
            use_copy = use.copy()

            hypocenter(seisvoronoi, center, reportseisesname_copy.copy(), sepoints_copy.copy(), senames_copy.copy(), 0, use_copy.copy())

            if prevuse != use:
                print("第", str(n), "报: ", "北纬", format(center.x, '.3f'), "东经", format(center.y, '.3f'))
                with open(r"static\log.json","w",encoding="utf-8") as f:
                    log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 第{n}报: 北纬{format(center.x, '.3f')} 东经{format(center.y, '.3f')}<br>"
                    json = "{\"LOG\":\"" + log + "\"}"
                    f.write(json)
                print(use)
                with open(r"static\sc_eew.json","w",encoding="utf-8") as f:
                    file_data = "{\"ID\": 111,\"EventID\": \"20240101070418" + str(n) + "\",\"ReportTime\": \"" + reporttime + "\",\"ReportNum\": " + str(n) + ",\"OriginTime\": \"" + reporttime + "\",\"HypoCenter\": \"架空模拟\",\"Latitude\": " + str(format(center.x, '.3f')) + ",\"Longitude\": " + str(format(center.y, '.3f')) + ",\"Magunitude\": " + str(mag) + ", \"Depth\": " + str(evdp) + ", \"Delta\": " + str(length(sepoints[senames.index(use[0])][0], sepoints[senames.index(use[0])][1], format(center.x, '.3f'), format(center.y, '.3f')) / 7.0) + "}"
                    f.write(file_data)
                n += 1
                if prevcenter != []:
                    if format(prevcenter.x, '.3f') == format(center.x, '.3f') and format(prevcenter.y, '.3f') == format(center.y, '.3f'):
                        print("锁定")
                        with open(r"static\log.json","w",encoding="utf-8") as f:
                            log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 震中锁定<br>"
                            json = "{\"LOG\":\"" + log + "\"}"
                            f.write(json)
                        prevcenter = center
                        prevuse = use
                        break
            prevcenter = center
            prevuse = use
            if prevcenter == []:
                if n == 1:
                    error = True
                    with open(r"static\log.json","w",encoding="utf-8") as f:
                        log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 第{n}报: 北纬{format(sepointsx[senames_copy.index(reportseisesname_copy[0])], '.3f')} 东经{format(sepointsy[senames_copy.index(reportseisesname_copy[0])], '.3f')}(首站)<br>"
                        json = "{\"LOG\":\"" + log + "\"}"
                        f.write(json)
                    with open(r"static\sc_eew.json","w",encoding="utf-8") as f:
                        file_data = "{\"ID\": 111,\"EventID\": \"20240101070418" + str(n) + "\",\"ReportTime\": \"" + reporttime + "\",\"ReportNum\": " + str(n) + ",\"OriginTime\": \"" + reporttime + f"\",\"HypoCenter\": \"架空模拟\",\"Latitude\": {format(sepointsx[senames_copy.index(reportseisesname_copy[0])], '.3f')},\"Longitude\": {format(sepointsy[senames_copy.index(reportseisesname_copy[0])], '.3f')},\"Magunitude\": " + str(mag) + ", \"Depth\": " + str(evdp) + ", \"Delta\": " + str(0) + "}"
                        f.write(file_data)
                    n += 1
                #print("数据错误")
                sepoints_copy.pop(senames_copy.index(reportseisesname_copy[0]))
                senames_copy.pop(senames_copy.index(reportseisesname_copy[0]))
                reportseisesname_copy.pop(0)
            seistrynum = 0
            center = []
            use = []
            if j == len(reportseisesname) - 1:
                #print("锁定(测站用尽惹)")
                break

            reportnum += 1
            #print("第" + str(reportnum) + "报: " + str(prevcenter))
    with open(r"static\log.json","w",encoding="utf-8") as f:
        log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 震中锁定<br>"
        json = "{\"LOG\":\"" + log + "\"}"
        f.write(json)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), reportseisesname[i] + ": 震中锁定，退出计算")
    return
t=Thread(target=cal)
t.start()
time.sleep(4)
for i in range(len(reportseisesname)):
    if i == 0:
        reporttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(r"static\log.json","w",encoding="utf-8") as f:
        log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 检测到震动 {reportseisesname[i]}<br>"
        json = "{\"LOG\":\"" + log + "\"}"
        f.write(json)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), reportseisesname[i] + ": 检测到震动")
    with open(r"static\seis.json","w",encoding="utf-8") as f:
        json = "{\"Lat\":\"" + str(sepointsx[senames.index(reportseisesname[i])]) + "\", \"Lon\":\"" + str(sepointsy[senames.index(reportseisesname[i])]) + "\"}"
        f.write(json)
    triggernum += 1
    if triggernum >= 3 and _open == False:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "确定地震事件发生，开始调查震中")
        with open(r"static\log.json","w",encoding="utf-8") as f:
            log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 确定事件发生，开始调查<br>"
            json = "{\"LOG\":\"" + log + "\"}"
            f.write(json)
            
        _open = True
    if triggernum > 20:     #减少计算
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), reportseisesname[i] + ": 计算程序退出，可开始新模拟")
        with open(r"static\log.json","w",encoding="utf-8") as f:
            log += f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 计算程序退出，可开始新模拟<br>"
            json = "{\"LOG\":\"" + log + "\"}"
            f.write(json)
            with open(r"static\switch.json","w",encoding="utf-8") as f:
                json = "{\"o\":1}"
                f.write(json)
            break
    time.sleep(reportseisestime[i])
