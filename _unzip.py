import tarfile
import os
import shutil
import concurrent.futures
import psutil
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
def unzip_file(file_name):
    tar = tarfile.open(file_name)
    names = tar.getnames()
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    #由于解压后是许多文件, 预先建立同名文件夹
    for name in names:
        tar.extract(name, file_name + "_files/")
    tar.close()

# 多线程解压文件
def process_directory(directory):
    # 获取所有需要解压的文件
    files_to_unzip = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) and item_path.endswith(('.gz')):
            files_to_unzip.append(item_path)

    # 根据 CPU 核心数调整线程池大小
    cpu_count = psutil.cpu_count(logical = False)
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("解压台站文件", total = len(files_to_unzip))
        with concurrent.futures.ThreadPoolExecutor(max_workers = cpu_count) as executor:
            futures = [executor.submit(unzip_file, file_path) for file_path in files_to_unzip]
            for future in concurrent.futures.as_completed(futures):
                future.result()
                progress.update(task, advance = 1)

def unzip():
    doc = "seis.tar"
    try:
        shutil.rmtree("seis.tar_files")
    except FileNotFoundError:
        pass
    unzip_file(doc)
    stinfo = []

    # 多线程解压
    process_directory(doc + '_files/')

    for filename in os.listdir(doc + '_files'):
        if filename[-8:] == "gz_files":
            stinfo.append(doc + '_files/' + filename + '/' + filename[:16] + ".EW")     #这里默认用东西走向数据

    return stinfo