# coding=gbk
'''
Created on 2015年11月28日

@author: 大雄
'''


from datetime import datetime
import getpass
import hashlib
from io import BytesIO
import json
import logging
import socket
from threading import Thread
import time

import xml.etree.ElementTree as ET
import command

def formatJsonRet(code=None, msg=None, data=None):
    class MyJsonEncoder(json.JSONEncoder):
        def default(self, o):
            if getattr(o, "toJsonString", None):
                return o.toJsonString()
            elif (isinstance(o, datetime)):
                return o.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return json.JSONEncoder.default(self, o)
    
    ret = {}
    ret["ret_code"] = code
    ret["ret_msg"] = msg
    ret["data"] = data
    return json.dumps(ret, cls=MyJsonEncoder)

def loadRet(dataset):
    ret = json.loads(dataset)
    return (ret.get("code"), ret.get("msg"), ret.get("data"))

def getClass(module_name, class_name):
    module_meta = __import__(module_name) 
    return getattr(module_meta, class_name) 

def getModule(module_name):
    return __import__(module_name) 
    
# def callSVN(cmd):    
#     flag1 = """Updated to revision"""
#     flag2 = """At revision"""
#     logging.info("execute:" + cmd)
#      
#     p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
#     line = p.stdout.readline()
#     message = None
#     revision = None
#     while(line):
#         lstr = line.decode()
#         if (lstr.find(flag1) > -1):
#             revision = (lstr.split(' '))[3][:-2]
#             message = lstr
#         if (lstr.find(flag2) > -1):
#             revision = (lstr.split(' '))[2][:-2]
#             message = lstr
#          
#         line = p.stdout.readline()
#          
#     p.communicate(timeout=60)
#     if p.returncode != 0:
#         raise ChildProcessError("callSVN Error: " + cmd + ", returncode: " + p.returncode)
#     else:
#         return message, revision
        
def md5str(v_str):
    m = hashlib.md5()
    m.update(v_str.encode())
    return m.hexdigest()        

def check_port(address, port, checktime=180):  
    sleeptime = 5
    if checktime < sleeptime:
        raise ValueError("checktime too small")
    
    check_count = checktime // sleeptime
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    count = 0
    while count < check_count:
        count = count + 1
        try:
            s.connect((address, port))
            s.shutdown(socket.SHUT_WR)
            s.close()
            return True
        except socket.error:
            pass
        time.sleep(sleeptime)
    logging.debug("check port timeout")
    # finally
    s.close() 
    return False

class CheckThread(Thread):
    retcode = None
    def __init__(self, address, port):
        self.address = address
        self.port = port
        Thread.__init__(self)
        
    def run(self):
        self.retcode = check_port(self.address, self.port)

class Namespace:
    pass

class SVNHelper:
    @staticmethod
    def getSVNLog(svn_path):
        try:
            cmd_svn_log = """svn log -r HEAD:1 {0} -l 5 --xml"""  
            # svn log
            cmd = cmd_svn_log.format(svn_path)
            stoutdata = command.callCommand(cmd)
        
            bio = BytesIO(stoutdata)
            tree = ET.parse(bio)
            #tree = ET.parse("d:\log.xml")
            root = tree.getroot()
            entries = []
            for logentry in root.findall("logentry"): 
                author = logentry.find('author').text   
                date = logentry.find('date').text
                msg = logentry.find('msg').text
                revision = logentry.get('revision')
                entries.append((revision, author, date, msg))
            return entries
        except Exception as e:
            logging.debug(e)
            return None
    
    @classmethod
    def getSVNLogByApp(cls, app):
        master_svn = app.getConfig("MASTER_SVN")
        config_svn = app.getConfig("CONFIG_SVN")
        app_svn_log = {"MASTER_SVN_LOG": cls.getSVNLog(master_svn)}
        if config_svn:
            app_svn_log["CONFIG_SVN_LOG"] = cls.getSVNLog(config_svn)
            
        return app_svn_log    
    
    @staticmethod
    def updateSVN(svn_path, svn_rev):
        cmd_svn_info = """svn info {0}"""
        cmd_svn_up = """svn update {0} -r {1}"""
        
        # svn update
        cmd = cmd_svn_up.format(svn_path, svn_rev)
        command.callCommand(cmd)
        
        # svn info
        cmd = cmd_svn_info.format(svn_path)
        stdoutdata = command.callCommand(cmd)
        svn_infos = {}
        for line in stdoutdata.decode().split("\n"):
            splits = line.split(":")
            if len(splits) < 1:
                break;
            left = splits[0].strip()
            right = "".join(splits[1:]).strip()
            svn_infos[left] = right
        return svn_infos

def waitCode2exitCode(waitCode):
    def bin2dec(string_num):
        return str(int(string_num, 2))

    def dec2bin(num):  
        tmp = "" 
        # 获取二进制字符串  
        while True:  
            tmp = tmp + str(num % 2)  
            num = num // 2  
            if num == 0:  
                break  
        tmp = list(tmp)  
        tmp.reverse()  
        tmp = "".join(tmp)  
        return tmp  
    return bin2dec(str(int(int(dec2bin(waitCode)) / 100000000)))

def getHostInfo():
    hostname = socket.gethostname()
    if hostname:
        ip = socket.gethostbyname(hostname)
        return (hostname, ip)
    else:
        return (None, None)
    
def getCurrentUser():
    return getpass.getuser()
