# coding=gbk
'''
Created on 2015年11月1日

@author: 大雄
'''

import datetime
import logging
import os

from command import callCommand
import command
from db import AppHistory
import env
from ucloud import BasicUCloudLib
from utils import SVNHelper
import utils


class AppDeploy:
   
    actionlist = []
    
    def __init__(self, app, servers):
        self.app = app
        self.servers = servers
        self.deploy_dir = env.config.get("APP_DEPLOY_DIR")
        self.temp_dir = env.config.get("APP_TEMP_DIR")
        self.numofversion = env.config.getint("NUMOFVERSION")
        self.is_archvie = env.config.getboolean("IS_ARCHVIE")
        
        self.actionlist.append(PackageAction(app, self))
        for server in servers:
            self.actionlist.append(DeployAction(app, server, self))
        if (self.is_archvie):
            self.actionlist(ArchiveAction(app, self))
            
        self.actionlist.append(RefreshUcdnAction(app, self))
            
    def deploy(self):
        self.__validator()
        for a in self.actionlist:
            a.action()
            
    def __validator(self):
        '''检查参数在当前环境是否有效'''
        if not os.path.isdir(self.deploy_dir):
            raise FileNotFoundError("deploy_dir dir not exist")
            
        if not os.path.isdir(self.temp_dir):
            raise FileNotFoundError("temp_dir dir not exist")
        
        if not os.path.isdir(self.app.getConfig("MASTER_SVN")):
            raise FileNotFoundError("dir: MASTER_SVN not exist")
        
        if  self.app.getConfig("CONFIG_SVN") and len(self.app.getConfig("CONFIG_SVN")) > 0 and not os.path.isdir(self.app.getConfig("CONFIG_SVN")):
            raise FileNotFoundError("dir: CONFIG_SVN not exist")
    
    def setAppStatus(self):
        # create config.get("APP_VERSION_FILE") file, update cache
        f = None
        try:
            status = {}
            status["BRAND"] = self.app.brand
            status["APP"] = self.app.name
            status["MASTER_REV"] = self.app.master_rev
            status["MASTER_URL"] = self.app.master_url
            status["CONFIG_REV"] = self.app.config_rev
            status["CONFIG_URL"] = self.app.config_url
            status["BUILDXML"] = self.app.getConfig("BUILDXML")
            # status["SERVER"] = app.server
            # status["HOME"] = app.module_home
            
            f = open(self.temp_dir + "/" + self.app.name + "/" + env.config.get("APP_VERSION_FILE"), "w")
            f.write(utils.formatJsonRet(data=status))
            '''update cache'''
            # key = self.app.brand + ":" + self.app.name + ":status"
            # RedisHelper.set(key, formatJsonRet(data=status))
        except Exception as e:
            logging.debug(e)
            logging.error("setAppStatus error")
        finally:
            f.close()

    def getAppStatus(self):
        # revision = RedisHelper.get(key)
        revision = None
        if (revision):  # 查找缓存
            return utils.loadRet(revision)[2]
        else:
            # 远程读取只读取第一台服务器的信息
            server = self.servers[0]
            path = server.webapp_home + "/" + self.app.getConfig("CONTEXT") + "/" + env.config.get("APP_VERSION_FILE")
            status = {}
            try:
                stdoutdata = command.createCommand(server.host, server.ssh_port, "cat " + path, type="SSH").execute()
                if stdoutdata:
                    status = utils.loadRet(stdoutdata.decode())[2]
                    # 写入缓存以便下次读取
                    # RedisHelper.set(key, formatJsonRet(data=status))
            except Exception as e:
                logging.debug(e)
                logging.debug("getAppStatus Error")
            return status
        
    def saveHistory(self):
        h = AppHistory()
        h.brand = self.app.brand
        h.name = self.app.name
        h.master_url = self.app.master_url
        h.master_rev = self.app.master_rev
        h.config_url = self.app.config_url
        h.config_rev = self.app.config_rev
        h.save(force_insert=True)
                           
def createAppDeploy(app, servers):    
    
    if not app:
        logging.error("app not exist")
        return None
    if not servers or len(servers) == 0:
        logging.error("server not exist")
        return None
    if not app.getConfig("CONTEXT"):
        logging.error("CONTEXT is missing")
        return None
    if not app.getConfig("MASTER_SVN"):
        logging.error("MASTER_SVN is missing")
        return None

    return AppDeploy(app, servers)

class AbstractAction:
    action_name = "Abstract Action"
    preaction = []
    postaction = []
    
    def _preAction(self):
        for t in self.preaction:
            t.action()
            
    def _postAction(self):
        for t in self.postaction:
            t.action()
    
    '''
         重写protected method _action(self)
    '''         
    def _action(self):
        logging.debug("action: " + self.action_name)

    def action(self):
        if len(self.preaction) > 0:
            self._preAction()
            
        self._action()
        
        if len(self.postaction) > 0:
            self._postAction()
 
class PackageAction(AbstractAction):
    
    def __init__(self, app, appdeploy):
        self.action_name = "Package Action"
        self.app = app
        self.appdeploy = appdeploy
        self.master_svn = self.app.getConfig("MASTER_SVN")
        self.config_svn = self.app.getConfig("CONFIG_SVN")
        self.master_rev = self.app.master_rev
        self.config_rev = self.app.config_rev
        self.temp_dir = self.appdeploy.temp_dir
        self.app_name = self.app.name
                
    def _action(self):
        AbstractAction._action(self)
        # 更新本地模块的svn版本
        svn_info = SVNHelper.updateSVN(self.master_svn, self.master_rev)
        m_rev = svn_info.get("Last Changed Rev")
        m_url = svn_info.get("URL")
        self.app.master_rev = m_rev
        self.app.master_url = m_url
        logging.info("Last Changed Rev:" + m_rev)
        # 同步本地模块的svn版本到临时目录
        command.createCommand(self.master_svn, None, self.temp_dir + "/" + self.app_name, type="RSYNC").execute()
                           
        if self.config_svn:
            # 更新本地模块配置的svn版本
            svn_info = SVNHelper.updateSVN(self.config_svn, self.config_rev)
            c_rev = svn_info.get("Last Changed Rev")
            c_url = svn_info.get("URL")
            self.app.config_url = c_url
            self.app.config_rev = c_rev
            logging.info("Last Changed Rev:" + c_rev)               
            # 覆盖临时目录的模块配置
            command.createCommand(self.config_svn + "/*", self.temp_dir + "/" + self.app_name + "/", type="COPY").execute()
            
class ArchiveAction(AbstractAction):
    
    def __init__(self, app, appdeploy):
        self.action_name = "Archive Action"
        self.appdeploy = appdeploy
        self.app = app
        self.brand = self.app.brand
        self.app_name = self.app.name
        self.deploy_dir = self.appdeploy.deploy_dir
        self.temp_dir = self.appdeploy.temp_dir
        self.numofversion = self.appdeploy.numofversion
    
    def _action(self):
        AbstractAction._action(self)
        time = datetime.datetime.now().strftime('%y%m%d%H%M');
        tag = self.brand + "_" + self.app_name 
        deploy_file = self.deploy_dir + "/" + tag + "_" + time + ".tar.gz"
        cmd = "/bin/tar zcf " + deploy_file + " -C " + self.temp_dir + " " + self.app_name
        def f(x):
            return x.find(tag) > -1
        
        callCommand(cmd)
    
        archives = list(filter(f, os.listdir(self.deploy_dir)))
        archives.sort()
        length = len(archives)
        
        numofversion = int(self.numofversion)
        if length > numofversion:
            for item in archives[0:length - numofversion - 1]:
                os.remove(self.deploy_dir + "/" + item)

class DeployAction(AbstractAction):    
    ftypes = [".jar", ".properties", ".xml"]        
    def __init__(self, app, server, appdeploy):
        self.action_name = "Deploy Action"
        self.app = app
        self.server = server
        self.appdeploy = appdeploy
        self.temp_dir = appdeploy.temp_dir
        self.context = app.getConfig("CONTEXT")
        self.app_name = app.name
        self.host = server.host
        self.ssh_port = server.ssh_port
        self.port = server.port
        self.webapp_home = server.webapp_home
        self.app_home = server.webapp_home + "/" + app.getConfig("CONTEXT")
        self.server_type = server.type
        
    
    def _action(self):
        AbstractAction._action(self)
        # 写入状态到本地和缓存
        self.appdeploy.setAppStatus()
        # 同步packaged 模块目录到各个服务器上    
        # 读取rsync同步结果，如果出现jar,或其他配置文件更新，则重启server
        outdata = command.createCommand(
                self.temp_dir + "/" + self.app_name, self.host, self.app_home, type="RSYNC").execute()
            # subprocess.call(cmd,shell=True)
            # 是否需要reload服务器
        if (env.config.getboolean("SERVER_DEFALUT_RELOAD") or self.checkfileUpdate(outdata, self.ftypes)):
            command.createCommand(self.host, self.ssh_port, "service " + self.server_type + " restart", type="SSH").execute()
            if env.config.getboolean("SERVER_RELOAD_SYNC") and self.port > 0:
                if not utils.check_port(self.host, self.port):
                    raise Exception("server not sync")
                else:
                    logging.debug("server sync")
    
    def checkfileUpdate(self, outdata, ftypes):
        outlines = outdata.decode().split("\n")
        # status = -1
        for line in outlines:
            logging.info("rsync Log: " + line)
#             if status < 0:
#                 if (line.find(self.header_of_inc_list) > -1):
#                     status = 0
#             else:
#                 for ftype in self.ftypes:
#                     if (line.find(ftype) > -1):
#                         return True
            for ftype in self.ftypes:
                if (line.find(ftype) > -1):
                    return True
        return False
    
class RefreshUcdnAction(AbstractAction):
    
    def __init__(self, app, appdeploy):
        self.action_name = "Refresh Ucdn Action"
        self.app = app
        self.appdeploy = appdeploy
        self.domainId = self.app.getConfig("DOMAINID")
        self.domainName = self.app.getConfig("DOMAINNAME")
        self.url = self.app.getConfig("URL")
        self.cdn_type = self.app.getConfig("CDN_TYPE")
                
    def _action(self):
        if self.cdn_type and self.cdn_type == "ucdn":
            ucloud = BasicUCloudLib()
            result = ucloud.refreshUcdnDomainCache(self.domainId, "file", self.url)
            logging.debug(result)
            if not result or not result.get("RetCode") or result["RetCode"] != 0:
                Exception("refresh Ucdn fail")
        else:
            logging.debug("No CDN Type:" + str(self.cdn_type))
    
