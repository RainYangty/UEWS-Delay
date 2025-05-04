import obspy
from obspy.signal.trigger import trigger_onset
from obspy.signal.trigger import classic_sta_lta, recursive_sta_lta, z_detect, carl_sta_trig
import time
import numpy as np
import json
import os
import psutil
import concurrent.futures
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
import threading

# 先读取配置文件捏
config = json.load(open("config.json", "r"))

# 创建线程锁
progress_lock = threading.Lock()

def process_station(i):
    try:
        # 尝试读取地震波形数据文件，如果文件存在则读取成功
        st = obspy.read(i)
    except FileNotFoundError:
        # 如果按照原始文件名读取失败，尝试添加后缀 "1" 后再读取
        st = obspy.read(i + "1")
    except:
        print("File Error")
        return None, None, None, None
    # 创建原始数据的副本，方便后续进行滤波等操作而不影响原始数据
    st2 = st.copy()
    # 对副本数据进行带通滤波，只保留频率在1.0Hz到10.0Hz之间的信号，目的可能是去除噪声等干扰，突出有效信号
    st2.filter("bandpass", freqmin=1.0, freqmax=10.0)
    # 获取滤波后数据的采样率，后续很多计算会基于这个采样率进行
    df = st2[0].stats.sampling_rate

    # 将时间字符串格式化为时间结构体，方便后续进行时间相关的计算。这里提取了波形数据起始时间的年、月、日、时、分、秒信息来构建时间结构体
    timeArray = time.strptime(str(st2[0].stats.starttime)[0:10] + " " + str(st2[0].stats.starttime)[11:19], "%Y-%m-%d %H:%M:%S")

    # 提前计算STA和LTA对应的样本点数
    if config["method"] in ["classic", "recursive"]:
        sta_samples = int(config["sta"] * df)
        lta_samples = int(config["lta"] * df)
    elif config["method"] == "z-detect":
        lta_samples = int(config["lta"] * df)
    else:
        sta_samples = int(0.5 * df)
        lta_samples = int(10 * df)

    # 根据配置文件中指定的方法选择相应的STA/LTA计算方式
    if config["method"] == "classic":
        cft = classic_sta_lta(st2[0].data, sta_samples, lta_samples)
    elif config["method"] == "recursive":
        cft = recursive_sta_lta(st2[0].data, sta_samples, lta_samples)
    elif config["method"] == "z-detect":
        cft = z_detect(st2[0].data, lta_samples)
    else:
        cft = classic_sta_lta(st2[0].data, sta_samples, lta_samples)

    # 使用trigger_onset函数根据计算得到的特征函数cft来检测触发时刻，触发阈值为3.5，返回的结果转换为numpy数组方便后续处理
    on_off = np.array(trigger_onset(cft, 3.5, 1))

    evdp = st2[0].stats.knet.evdp  # 获取震源深度信息，从数据的相关属性中提取
    mag = st2[0].stats.knet.mag  # 获取震级信息，同样从数据的对应属性中获取

    # 如果检测到了触发时刻（即on_off数组有元素）
    if on_off.size > 0:
        # 计算P波到时对应的时间，通过将触发时刻对应的索引（以样本点数表示）除以采样率转换为以秒为单位的时间
        Ptime = on_off[:, 0] / df
        return st2[0].stats.station, time.mktime(timeArray) + Ptime[0], evdp, mag
    return None, None, evdp, mag

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
    results = []
    cpu_count = psutil.cpu_count(logical=False)
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("台站数据分析", total=len(sta))
        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
            futures = [executor.submit(process_station, i) for i in sta]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result[0] is not None:
                    results.append(result)
                with progress_lock:
                    progress.update(task, advance=1)

    # 按P波到时排序
    results.sort(key=lambda x: x[1])
    seisname = [result[0] for result in results]
    seistime = [result[1] for result in results]
    evdp = results[0][2] if results else 0
    mag = results[0][3] if results else 0

    return seisname, seistime, evdp, mag
            
    


# 调用sortseis函数，传入一个包含地震波形数据文件路径的列表，这里只传入了一个文件路径作为示例，实际应用中可以传入多个文件路径
# sortseis(["seis.tar_files\CHB0082412041911.tar.gz_files\CHB0082412041911.EW"])