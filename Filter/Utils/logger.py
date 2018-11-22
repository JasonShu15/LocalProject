#coding:utf-8
import os
import logging
import pandas as pd
from Utils.config import log_root_path


def set_logger(name):
    if name=='forecast':
        path = log_root_path + 'forecast_%s.txt' % pd.datetime.now().strftime('%Y%m%d')
    elif name=='train':
        path = log_root_path + 'train_%s.txt' % pd.datetime.now().strftime('%Y%m%d')
    elif name=='report':
        path = log_root_path + 'report_%s.txt' % pd.datetime.now().strftime('%Y%m%d')
    else:
        raise Exception("Wrong log name!")
    if not os.path.exists(log_root_path):
        os.makedirs(log_root_path)
    # 创建一个logger,可以考虑如何将它封装
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(path)
    fh.setLevel(logging.ERROR)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)d] - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
