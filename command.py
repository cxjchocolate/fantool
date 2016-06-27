# coding=gbk
'''
Created on 2016年1月23日

@author: 大雄
'''
import logging
import os
import select
import signal
import subprocess

import utils


class AbstractCommand:
    cmd = None
    def execute(self):
        logging.info("execute:" + self.cmd)
        p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdoutdata, stderrdata) = p.communicate(timeout=60)
        if p.returncode != 0:
            raise ChildProcessError(stderrdata.decode())
        return stdoutdata
        
class SSHCommand(AbstractCommand):
    def __init__(self, host, port, command):
        cmd_template = """ssh -p {1} {0} '{2}'"""
        self.cmd = cmd_template.format(host, port, command)
        
class RsyncCommand(AbstractCommand):
    def __init__(self, local_path, remote_host, remote_path):
        cmd_template = """rsync -azP --delete --exclude logs --exclude *.log --exclude */*.log --exclude .svn --exclude WEB-INF/wx-conf/zaofans.com {0}/  {1}:{2}/"""
        cmd_template2 = """rsync -azP --delete --exclude logs --exclude *.log --exclude */*.log --exclude .svn --exclude WEB-INF/wx-conf/zaofans.com {0}/  {1}/"""
        
        if remote_host:
            self.cmd = cmd_template.format(local_path, remote_host, remote_path)
        else:
            self.cmd = cmd_template2.format(local_path, remote_path)

class CopyCommand(AbstractCommand):
    def __init__(self, src, target):
        cmd_template = """cp -rp {0} {1}"""
        self.cmd = cmd_template.format(src, target) 

class SCPCommand(AbstractCommand):
    def __init__(self, src, remote, remote_port, target):
        cmd_template = """scp -r -P {2} {0} {1}:{3}"""
        self.cmd = cmd_template.format(src, remote, remote_port, target) 
          
def createCommand(*args, **kargs):
    cmd_type = kargs.get("type")
    if not cmd_type:
        raise Exception("Command type not define")
    if cmd_type == 'SSH':
        return SSHCommand(*args)
    if cmd_type == "RSYNC":
        return RsyncCommand(*args)
    if cmd_type == "COPY":
        return CopyCommand(*args)
    if cmd_type == "SCP":
        return SCPCommand(*args)
    
def callCommand(cmd):
        logging.info("execute:" + cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdoutdata, stderrdata) = p.communicate(timeout=60)
        if p.returncode != 0:
            raise ChildProcessError(stderrdata.decode())
        return stdoutdata
    
def packApp(buildxml, version, socket):
    pack_cmd = "sh /data/svn/Deploy/trunk/fantool/bin/pack.sh {0} {1}"
    cmd = pack_cmd.format(buildxml, version)
    __writeSocket(cmd, socket)
        
def __writeSocket(cmd, socket, timeout=60):
    logging.info(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    
    try:
        while 1:       
            f = select.select([p.stdout], [], [], timeout)
            if p.stdout in f[0]:
                line = p.stdout.readline()
                if line:
                    socket.write_message(utils.formatJsonRet(msg=line.decode()))
                else:
                    # socket.write_message(getConfig.formatJsonRet(msg="return code: " + p.returncode))
                    socket.write_message(utils.formatJsonRet(code="success", msg="success"))
                    break
            else:
                socket.write_message(utils.formatJsonRet(code="error", msg="return code: timeout " + str(timeout) + "s"))
                logging.info(os.kill(p.pid, signal.SIGILL))
                break
    except Exception as e:
        logging.debug(e)
        socket.write_message(utils.formatJsonRet(code="error", msg=str(e)))
