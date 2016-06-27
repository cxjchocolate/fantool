# coding=gbk
'''
Created on 2016��1��23��

@author: ����
'''

import configparser
import os
import sys


config = None
def configure(file): 
    if not os.path.exists(sys.path[0] + "/conf/" + file):
        raise FileNotFoundError("conf file not exists: " + sys.path[0] + "/conf/" + file)
    
    c = configparser.ConfigParser()
    c.read(sys.path[0] + "/conf/" + file, "utf8")
    global config
    config = c["DEFAULT"]
