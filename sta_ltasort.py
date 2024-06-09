import obspy
from obspy.signal.trigger import trigger_onset
from obspy.signal.trigger import classic_sta_lta, recursive_sta_lta, z_detect, carl_sta_trig
import time
import numpy as np
import json

#先读取配置文件捏
config = json.load(open("config.json", "r"))

"""
本函数捏实现哩运用STA/LTA算法进行对台站触发顺序进行排序
"""
def sortseis(sta):
    seistime = []
    seisname = []
    evdp = 0
    mag = 0
    op = False

    for i in sta:
        try:
            st = obspy.read(i)
        except FileNotFoundError:
            st = obspy.read(i + "1")
        except:
            print("File Error")
            break
        st2 = st.copy()
        st2.filter("bandpass",freqmin=1.0, freqmax=10.0)
        df = st2[0].stats.sampling_rate
        # print(st2[0].stats.starttime)
        timeArray = time.strptime(str(st2[0].stats.starttime)[0:10] + " " + str(st2[0].stats.starttime)[11:19], "%Y-%m-%d %H:%M:%S")
        # print(timeArray)
        # print(time.mktime(timeArray))
        # set the STA=5 seconds, LTA=20 seconds
        if (config["method"] == "classic"):
            cft = classic_sta_lta(st2[0].data, int(config["sta"] * df), int(config["lta"] * df))
        if (config["method"] == "recursive"):
            cft = recursive_sta_lta(st2[0].data, int(config["sta"] * df), int(config["lta"] * df))
        if (config["method"] == "z-detect"):
            cft = z_detect(st2[0].data, int(config["lta"] * df))
        else:
            cft = classic_sta_lta(st2[0].data, int(0.5 * df), int(10 * df))
        
        # set the trigger threshold=1.5, detrigger threshold=0.27
        df = st2[0].stats.sampling_rate
        
        on_off = np.array(trigger_onset(cft, 3.5, 1))
        evdp = st2[0].stats.knet.evdp
        mag = st2[0].stats.knet.mag

        # print(st2[0].stats.station)
        if on_off.size > 0:
            Ptime = on_off[:, 0] / df
            # print(time.mktime(timeArray) + Ptime[0])
            if op:
                if seistime[0] > time.mktime(timeArray) + Ptime[0]:
                    seistime.insert(0, time.mktime(timeArray) + Ptime[0])
                    seisname.insert(0, st2[0].stats.station)
                elif seistime[-1] < time.mktime(timeArray) + Ptime[0]:
                    seistime.append(time.mktime(timeArray) + Ptime[0])
                    seisname.append(st2[0].stats.station)
                else:
                    for t in range(len(seistime) - 1):
                        if seistime[t] < time.mktime(timeArray) + Ptime[0] and seistime[t + 1] > time.mktime(timeArray) + Ptime[0]:
                            seistime.insert(t + 1, time.mktime(timeArray) + Ptime[0])
                            seisname.insert(t + 1, st2[0].stats.station)
                            break
            else:
                seistime.append(time.mktime(timeArray) + Ptime[0])
                seisname.append(st2[0].stats.station)
                op = True
                # plot_trigger(st2[0], cft, 1.5, 0.27)
        """ else:
            print("Error") """

    #print(seistime)
    #print(seisname)
    return seisname, seistime, evdp, mag