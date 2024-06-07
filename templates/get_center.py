from unzip import unzip
from sta_ltasort import sortseis
from scipy.spatial import Voronoi
import numpy as np
from shapely.geometry import Polygon
import shapely
import numpy as np
import time

#seislink = unzip()

#reportseisesname, reportseisestime = sortseis(seislink)

ok = False

def hypocenter(prev, prev_center, reportseis, allseis, allseisname, ii, useseis, seistrynum):
    global ok
    global center, use
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
    #print(ii, prev.centroid)
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

def get(reportseisesname):
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
    prevcenter = []
    prevuse = []
    center = []
    use = []
    seistrynum = 0

    reportseisesname_copy = reportseisesname.copy()
    sepoints_copy = sepoints.copy()
    senames_copy = senames.copy()
    use_copy = use.copy()

    hypocenter(seisvoronoi, center, reportseisesname_copy.copy(), sepoints_copy.copy(), senames_copy.copy(), 0, use_copy.copy(), seistrynum)

    if prevuse != use:
        if prevcenter != []:
            if format(prevcenter.x, '.3f') == format(center.x, '.3f') and format(prevcenter.y, '.3f') == format(center.y, '.3f'):
                print("锁定")
                prevcenter = center
                prevuse = use
                return center
    prevcenter = center
    prevuse = use
    if prevcenter == []:
        #print("数据错误")
        sepoints_copy.pop(senames_copy.index(reportseisesname_copy[0]))
        senames_copy.pop(senames_copy.index(reportseisesname_copy[0]))
        reportseisesname_copy.pop(0)
    center = []
    use = []