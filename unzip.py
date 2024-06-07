import tarfile
import os
import shutil
def un_tar(file_name):
    tar = tarfile.open(file_name)
    names = tar.getnames()
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    #由于解压后是许多文件，预先建立同名文件夹
    for name in names:
        tar.extract(name, file_name + "_files/")
    tar.close()

"""
本函数用来解压NIDE公开的测站数据
"""
def unzip():
    doc = "seis.tar"
    try:
        shutil.rmtree("seis.tar_files")
    except FileNotFoundError:
        pass
    un_tar(doc)
    stinfo = []

    for filename in os.listdir(doc + '_files'):
        if filename[-3:] == ".gz":
            un_tar(doc + '_files/' + filename)
    for filename in os.listdir(doc + '_files'):
        if filename[-8:] == "gz_files":
            #print(filename)
            stinfo.append(doc + '_files/' + filename + '/' + filename[:16] + ".EW")     #这里默认用东西走向数据

    return stinfo