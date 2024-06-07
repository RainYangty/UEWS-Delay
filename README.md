# Unofficial Earthquake (Delay) Warning System | 非官方地震架空模拟系统
🌐 开源的地震信息架空模拟系统

## 功能
- 本地基于Voronoi图计算震中所处区域
- P/S波预计运动模拟
- P/S波预计抵达时间提示
- 自定位置横波抵达倒数、烈度粗估

## 免责申明

UEWS和Rain Yang 不会自行对众发布地震预警/地震速报信息。其地震架空模拟信息来源为用户自行上传的地震站数据

## 注意

UEWS仅支持对日本NIDE公开的地震站数据信息进行震中计算

UEWS 目前并不稳定、完善，随时可能崩溃，若遇到问题，欢迎提交Issue。若因UEWS不稳定导致并未及时发出来自四川地震局公开的「紧急地震信息」地震预警数据，在这里深感歉意捏

## 部署
安装依赖
```
pip install -r requirements.txt
```
运行
```
python main.py
```

## 协议
本仓库代码依据MIT License协议开源
