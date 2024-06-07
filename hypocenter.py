from unzip import unzip
from sta_ltasort import sortseis
from scipy.spatial import Voronoi
from shapely.geometry import Polygon
import numpy as np
import shapely
import sys

log = ""
try:
    seislink = unzip()

    reportseisesname, reportseisestime, evdp, mag = sortseis(seislink)
    reseis = reportseisesname.copy()
    print("数据收集完毕，开始计算")

    benchmark = reportseisestime[0]
    for i in range(len(reportseisestime)):
        reportseisestime[i] -= benchmark
except:
    print("输入不合规")
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
ok = False
seistrynum = 0
reportnum = 0
prevcenter = []
prevuse = []
n = 1
lock = 0
reporttime = 0
error = False

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

def cal():
    global ok, sepoints, senames, evdp, mag, log, error
    global center, use, seistrynum, prevcenter, prevuse, reportnum, n, reporttime, triggernum
    reportseisesname_copy = reportseisesname.copy()
    sepoints_copy = sepoints.copy()
    senames_copy = senames.copy()
    use_copy = use.copy()

    hypocenter(seisvoronoi, center, reportseisesname_copy.copy(), sepoints_copy.copy(), senames_copy.copy(), 0, use_copy.copy())
    if (center != []):
        print("北纬", format(center.x, '.3f'), "东经", format(center.y, '.3f'))
    else:
        print("北纬", sepointsx[senames.index(reseis[0])], "东经", sepointsy[senames.index(reseis[0])], "(首触发站)")
cal()