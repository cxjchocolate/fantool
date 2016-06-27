# coding=gbk
'''
Created on 2015年12月26日

@author: 大雄
'''
import logging
import os
import select
import signal
import sys
import time

from peewee import datetime

import app as appmodule
import command
from db import App, Server, RedisHelper, Operation, Script, Host, AppHistory
import env
from utils import SVNHelper
import utils


def deployApp(brand, app, master_rev, config_rev):
    try :
        app_instance = App.get(App.brand == brand, App.name == app)
        app_instance.master_rev = master_rev
        app_instance.config_rev = config_rev
        servers = Server.raw(
          '''select * from t_server where id in ({0})'''.format(app_instance.getConfig("SERVERS"))
        )    
        #     if prd:
        #         profile = DBHelper().getProfile("prd")
        #     else:
        #         profile = DBHelper().getProfile("dev")

        deploy_instance = appmodule.createAppDeploy(app_instance, [s for s in servers])
        if deploy_instance:
            deploy_instance.deploy()
            deploy_instance.saveHistory()
            return None
        else:
            raise Exception("None Object AppDeploy")
    except Exception as e:
        logging.debug(e)
        raise Exception("app deploy fail:" + str(e))

def rollbackApp(brand, app):
    apps = AppHistory.select().where(
                                     AppHistory.brand == brand and AppHistory.name == app
                                     ).order_by(-AppHistory.createtime).limit(2)
    if len(apps) != 2:
            raise Exception("only one history has been found. Cannot rollback")
    app = apps[1]  
    yesorno = input('RollBack App:' + "\n"
                    + " Brand: " + app.brand + "\n" 
                    + " App: " + app.name + "\n"
                    + " Master rev: " + app.master_rev + "\n" 
                    + " Config rev: " + app.config_rev +"\n"
                    + " CreateTime: " + str(app.createtime) + "\n" 
                    + " (Y/N)")
    if yesorno =="Y":
        print("Starting RollBack...")
        #deployApp(brand, app, apps[1].master_rev, apps[1].config_rev)
    elif yesorno =="N":
        print("End RollBack")
    else:
        print("Wrong Input!")
        
def infoApp(brand, app):
    try :
        app = App.get(App.brand == brand, App.name == app)
        servers = Server.raw(
          '''select * from t_server where id in ({0})'''.format(app.getConfig("SERVERS"))
        )    

        deploy = appmodule.createAppDeploy(app, [s for s in servers])
        if deploy:
            app_status = deploy.getAppStatus()
            if len(app_status.keys()) > 0:
                return app_status
            else:
                return None
        else:
            raise Exception("None Object appdeploy")
    except Exception as e:
        logging.debug(e)
        raise Exception("infoApp: " + str(e))

def keysMem(brand, server):
    try:
        server1 = Server.getServer(brand, server)
        if server1:
            out = RedisHelper.keys(server1.host)
            return out
        else:
            raise Exception("None Object Server")
    except Exception as e:
        logging.debug(e)
        raise Exception("keysMem: " + str(e))

def flushMem(brand, server): 
    try:
        servername = server + "." + brand
        server1 = Server.get(Server.name == servername)
        if server1:
            out = RedisHelper.flushdb(server1.host)
            return  out
        else:
            raise Exception("None Object Host")
    except Exception as e:
        logging.debug(e)
        raise Exception("flushMem:" + str(e))
       
def stopServer(brand, name):
    try:
        server1 = Server.getServer(brand, name)
        command.createCommand(server1.host, server1.ssh_port, "service " + server1.type + " stop", type="SSH").execute()
        return None
    except Exception as e:
        logging.debug(e)
        raise Exception("stopServer: " + str(e))
    
def getSVNLog(brand, app):
    try :
        app = App.get(App.brand == brand, App.name == app)
        if app:
            return SVNHelper.getSVNLogByApp(app)
        else:
            raise Exception("None Object App")
    except Exception as e:
        logging.debug(e)
        raise Exception("getSVNLog: " + str(e))

def startServer(brand, name):
    try:
        server1 = Server.getServer(brand, name)
        command.createCommand(server1.host, server1.ssh_port, "service " + server1.type + " start", type="SSH").execute()
        return None
    except Exception as e:
        logging.debug(e)
        raise Exception("startServer: " + str(e))
    
def restartServer(brand, name):
    try:
        server1 = Server.getServer(brand, name)
        command.createCommand(server1.host, server1.ssh_port, "service " + server1.type + " restart", type="SSH").execute()
        if (env.config.getboolean("SERVER_RELOAD_SYNC")):
            if checkServer(brand, name):
                return None
            else:
                raise Exception("server not sync")
        else:
            return None
    except Exception as e:
        logging.debug(e)
        raise Exception("restartServer: " + str(e))

def checkServers(brand, app):
    try :
        app = App.get(App.brand == brand, App.name == app)
        servers = Server.raw(
          '''select * from t_server where id in ({0})'''.format(app.getConfig("SERVERS"))
        ) 
        
        check_list = []
        for server in servers:
            th = utils.CheckThread(server.host, server.port)
            check_list.append(th)
            th.start()
        for th in check_list:
            th.join()
        time.sleep(2)
        flag = True
        for th in check_list:
            flag = flag and th.retcode
        return flag         
    except Exception as e:
        logging.debug(e)
        logging.debug("server not exist, check server fails:" + str(e))
        return False
    
def checkServer(brand, name):
    try:
        server = Server.getServer(brand, name)
        return utils.check_port(server.host, server.port)
    except Exception:
        logging.debug("server not exist, check server fails")
        return False

def runScript(script_id, host_id):
    s = Script.getScript(script_id)
    h = Host.getHost(host_id)
    filename = "/tmp/script_" + str(script_id)
    with open(filename, "wb") as file:
        file.write(s.content)
    try:
        command.createCommand(filename, h.ip, h.ssh_port, filename, type="SCP").execute()
        command.createCommand(h.ip, h.ssh_port, "sh " + filename, type="SSH").execute()
        return "success"
    except:
        return "false"
    
class OpenAPI():
    def __init__(self, module_name, class_name, method_name, *args, **kargs):
        self.module_name = module_name
        self.class_name = class_name
        self.method_name = method_name
        self.args = kargs.get("args")
        self.env = kargs.get("env")
    
    # env is a namespace
    # including some env parameters            
    def __call(self):
        try:
            op = self.__loggingOpenAPI()
            if self.class_name:
                cls = utils.getClass(self.module_name, self.class_name)
                o = getattr(cls, self.method_name)
            else:
                mod = utils.getModule(self.module_name)
                o = getattr(mod, self.method_name)
            # 设置开始时间
            op.start_time = datetime.datetime.now()
            # 执行任务
            ret = o(*self.args)
            # 设置结束时间
            op.end_time = datetime.datetime.now()
            # 强制写入operation log
            #op.save(force_insert=False)
            # 返回结果
            return 0, "success", ret
        except Exception as e:
            logging.debug(e)
            return 1, str(e), None
            
    def __loggingOpenAPI(self):
        op = Operation()
        if self.class_name:
            op.name = self.module_name + "." + self.class_name + "." + self.method_name
        else:
            op.name = self.module_name + "." + self.method_name
        op.data = str(self.args)
        op.machine = self.env.machine
        op.ipaddr = self.env.ipaddr
        op.username = self.env.username
        op.program = self.env.program
        return op    
        
    def socketCall(self, socket, timeout=60):
        try:
            readEnd, writeEnd = os.pipe()
            # windows平台上没有fork的api
            pid = os.fork()
            # parent process, pid是child pid
            if pid > 0:
                # 关闭parent pipe write
                os.close(writeEnd)
                readFile = os.fdopen(readEnd)
                while 1:       
                    f = select.select([readFile], [], [], timeout)
                    if readFile in f[0]:
                        line = readFile.readline()
                        if line:
                            socket.write_message(utils.formatJsonRet(msg=line))
                        else:
                            break
                    else:
                        logging.debug("timeout " + str(timeout) + "s")
                        os.kill(pid, signal.SIGILL)
                        break
                    
                fork_proc_exitCode = utils.waitCode2exitCode(os.waitpid(pid, 0)[1])
                if fork_proc_exitCode == "0":
                    socket.write_message(utils.formatJsonRet(code="success", msg="return code:" + fork_proc_exitCode))
                else:
                    socket.write_message(utils.formatJsonRet(code="error", msg="return code:" + fork_proc_exitCode))
                
            # child process
            if pid == 0:
                os.close(readEnd)
                os.dup2(writeEnd, sys.stdout.fileno())
                os.dup2(writeEnd, sys.stderr.fileno())
                os.close(writeEnd)
                response = self.__call()
                print(response[1])
                os._exit(response[0])
        except os.error as e:
            logging.debug(e)
            raise Exception("fork process fail")
            
    def call(self):
        response = self.__call()
        print(response[1])

    def webCall(self, request, timeout=60):
        response = self.__call()
        request.write(utils.formatJsonRet(response[0], response[1], response[2]))

if __name__ == '__main__':
    runScript(13, "192.168.46.102")