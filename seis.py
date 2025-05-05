# https://www.kyoshin.bosai.go.jp/kyoshin/pubdata/all/sitedb/sitepub_all_en.csv

import requests
import obspy
from rich.progress import Progress

def updated_one_seis(station_name, seislink):
    station_path = filter(lambda x: station_name in x, seislink)
    station_path = list(station_path)
    st = 0
    try:
        # 尝试读取地震波形数据文件，如果文件存在则读取成功
        st = obspy.read(station_path[0])
    except FileNotFoundError:
        # 如果按照原始文件名读取失败，尝试添加后缀 "1" 后再读取
        st = obspy.read(station_path[0] + "1")
    except:
        print("File Error")
        return None, None
    return st.traces[0].stats.knet.stla, st.traces[0].stats.knet.stlo
    
# updated_one_seis("AIC001", ["seis.tar_files/AIC0012401011610.tar.gz_files/AIC0012401011610.EW"])