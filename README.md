# Unofficial Earthquake (Delay) Warning System | 非官方地震架空模拟系统
🌐 开源的地震信息架空模拟系统

## 功能
- 本地基于Voronoi图计算震中所处区域
- P/S波预计运动模拟
- P/S波预计抵达时间提示
- 自定位置横波抵达倒数、烈度粗估
- 网页界面仿照 CEIV1.0.3

## 免责申明

UEWS和Rain Yang不会自行对众发布地震预警/地震架空模拟信息。其地震架空模拟信息来源为用户自行上传的地震站数据

## 注意

UEWS仅支持对日本NIDE公开的地震站数据信息进行震中计算，且最终震中应以官方公布为准

本程序使用Voronoi图的方法进行计算，由于算法问题效率并不高且精度有待提高呐

NIDE测站数据及位置来源于 https://www.kyoshin.bosai.go.jp/kyoshin/db/index_en.html?all

UEWS 目前并不稳定、完善，随时可能崩溃，若遇到问题，欢迎提交Issue。

## 部署
务必先cd进入程序文件夹！！！
### 安装依赖
```
pip install -r requirements.txt
```
### 运行架空模拟
注：此无需提前将NIDE下载的测站.tar文件数据放在程序同级文件夹中，且无需解压
```
python main.py
```
访问网页后左下角点击"上传"，将下载的.tar文件上传

### 仅计算地震
注：此必须提前将NIDE下载的测站.tar文件数据放在程序同级文件夹中，但无需解压
```
python hypocenter.py
```

## 协议
本仓库代码依据Apache 2.0协议开源
