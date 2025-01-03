import obspy
from obspy.signal.trigger import trigger_onset
from obspy.signal.trigger import classic_sta_lta, recursive_sta_lta, z_detect, carl_sta_trig
import time
import numpy as np
import json

# 先读取配置文件捏
config = json.load(open("config.json", "r"))

def sortseis(sta):
    """
    运用STA/LTA算法进行对台站触发顺序进行排序

    参数:
    sta(list):      地震站波形数据位置

    返回:
    seisname(list): 排好顺序后的地震站名称
    seistime(list): P波到时对应时间戳
    evdp(float):    从文件中获取到的震源深度
    mag(float):     从文件中获取到的震级
    """
    seistime = []  # 用于存储每个台站检测到的P波到时对应的时间戳
    seisname = []  # 用于存储台站名称
    evdp = 0  # 初始化震源深度，后续会进行赋值
    mag = 0  # 初始化震级，后续会进行赋值
    op = False  # 一个标志位，用于判断是否是第一次添加数据到seistime和seisname列表中

    for i in sta:
        try:
            # 尝试读取地震波形数据文件，如果文件存在则读取成功
            st = obspy.read(i)
        except FileNotFoundError:
            # 如果按照原始文件名读取失败，尝试添加后缀 "1" 后再读取
            st = obspy.read(i + "1")
        except:
            print("File Error")
            break
        # 创建原始数据的副本，方便后续进行滤波等操作而不影响原始数据
        st2 = st.copy()
        # 对副本数据进行带通滤波，只保留频率在1.0Hz到10.0Hz之间的信号，目的可能是去除噪声等干扰，突出有效信号
        st2.filter("bandpass", freqmin=1.0, freqmax=10.0)
        # 获取滤波后数据的采样率，后续很多计算会基于这个采样率进行
        df = st2[0].stats.sampling_rate

        # 将时间字符串格式化为时间结构体，方便后续进行时间相关的计算。这里提取了波形数据起始时间的年、月、日、时、分、秒信息来构建时间结构体
        timeArray = time.strptime(str(st2[0].stats.starttime)[0:10] + " " + str(st2[0].stats.starttime)[11:19], "%Y-%m-%d %H:%M:%S")

        # 根据配置文件中指定的方法选择相应的STA/LTA计算方式
        if (config["method"] == "classic"):
            # 使用classic_sta_lta方法计算特征函数（Characteristic Function），传入的数据长度根据配置文件中的sta和lta参数以及采样率来确定，
            # 这两个参数通常用于控制短期平均（STA）和长期平均（LTA）的时间窗口长度，以样本点数为单位
            cft = classic_sta_lta(st2[0].data, int(config["sta"] * df), int(config["lta"] * df))
        elif (config["method"] == "recursive"):
            # 类似地，使用recursive_sta_lta方法计算特征函数，不同的STA/LTA计算方法可能在计算效率、对信号变化的适应性等方面有所差异
            cft = recursive_sta_lta(st2[0].data, int(config["sta"] * df), int(config["lta"] * df))
        elif (config["method"] == "z-detect"):
            # 使用z_detect方法计算特征函数
            cft = z_detect(st2[0].data, int(config["lta"] * df))
        else:
            # 如果配置文件中指定的方法不匹配上述几种情况，则使用默认的classic_sta_lta方法，并设置特定的STA和LTA窗口对应的样本点数
            cft = classic_sta_lta(st2[0].data, int(0.5 * df), int(10 * df))

        # 使用trigger_onset函数根据计算得到的特征函数cft来检测触发时刻，触发阈值为3.5，返回的结果转换为numpy数组方便后续处理
        on_off = np.array(trigger_onset(cft, 3.5, 1))

        evdp = st2[0].stats.knet.evdp  # 获取震源深度信息，从数据的相关属性中提取
        mag = st2[0].stats.knet.mag  # 获取震级信息，同样从数据的对应属性中获取

        # 如果检测到了触发时刻（即on_off数组有元素）
        if on_off.size > 0:
            # 计算P波到时对应的时间，通过将触发时刻对应的索引（以样本点数表示）除以采样率转换为以秒为单位的时间
            Ptime = on_off[:, 0] / df
            # print(time.mktime(timeArray) + Ptime[0])
            # print(Ptime[0])
            if op:
                # 如果不是第一次添加数据到seistime和seisname列表中（即op为True）
                if seistime[0] > time.mktime(timeArray) + Ptime[0]:
                    # 如果当前检测到的P波到时比已记录的最早P波到时还早
                    # 将当前P波到时插入到seistime列表的最前面，同时将对应的台站名称插入到seisname列表的最前面
                    seistime.insert(0, time.mktime(timeArray) + Ptime[0])
                    seisname.insert(0, st2[0].stats.station)
                elif seistime[-1] < time.mktime(timeArray) + Ptime[0]:
                    # 如果当前检测到的P波到时比已记录的最晚P波到时还晚
                    # 将当前P波到时添加到seistime列表的末尾,同时将对应的台站名称添加到seisname列表的末尾
                    seistime.append(time.mktime(timeArray) + Ptime[0])
                    seisname.append(st2[0].stats.station)
                else:
                    # 如果当前P波到时处于已记录的时间中间
                    # 遍历seistime列表（除最后一个元素外）
                    for t in range(len(seistime) - 1):
                        if seistime[t] < time.mktime(timeArray) + Ptime[0] and seistime[t + 1] > time.mktime(timeArray) + Ptime[0]:
                            # 如果当前P波到时大于列表中某个时刻且小于下一个时刻，说明找到了合适的插入位置
                            # 将当前P波到时插入到合适位置,同时插入对应的台站名称
                            seistime.insert(t + 1, time.mktime(timeArray) + Ptime[0])
                            seisname.insert(t + 1, st2[0].stats.station)
                            break  # 插入后就跳出循环
            else:
                # 如果是第一次添加数据
                # 将当前P波到时添加到seistime列表,将对应的台站名称添加到seisname列表
                seistime.append(time.mktime(timeArray) + Ptime[0])
                seisname.append(st2[0].stats.station)
                # 将op标志位设为True，表示已经添加过数据了，后续就按非第一次的逻辑处理
                op = True
    return seisname, seistime, evdp, mag


# 调用sortseis函数，传入一个包含地震波形数据文件路径的列表，这里只传入了一个文件路径作为示例，实际应用中可以传入多个文件路径
# sortseis(["seis.tar_files\CHB0082412041911.tar.gz_files\CHB0082412041911.EW"])