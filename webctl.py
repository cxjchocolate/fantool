# coding=gbk

import json
import logging

import tornado.ioloop
import tornado.websocket

import app
import command
import env
from openapi import OpenAPI, getSVNLog
import utils


def getenv(requestHandler):
    e = utils.Namespace()
    setattr(e, "machine", "")
    setattr(e, "ipaddr", requestHandler.request.remote_ip)
    setattr(e, "username", "")
    setattr(e, "program", "webctl") 
    return e

class flushmem(tornado.web.RequestHandler):
    def get(self, brand, server):
        OpenAPI("openapi", None, "flushMem", args=(brand, server), env=getenv(self)).webCall(self)

class keysmem(tornado.web.RequestHandler):
    def get(self, brand, server):
        OpenAPI("openapi", None, "keysMem", args=(brand, server), env=getenv(self)).webCall(self)        

class infoapp(tornado.web.RequestHandler):
    def get(self, brand, app):
        OpenAPI("openapi", None, "infoApp", args=(brand.upper(), app.upper()), env=getenv(self)).webCall(self)    

class getSVNLog(tornado.web.RequestHandler):
    def get(self, brand, app):
        OpenAPI("openapi", None, "getSVNLog", args=(brand.upper(), app.upper()), env=getenv(self)).webCall(self)    

class Script(tornado.web.RequestHandler):
    def get(self, script_id):
        if script_id == "showall":
            OpenAPI("db", "Script", "getAllScripts", args=(), env=getenv(self)).webCall(self)
        else:
            OpenAPI("db", "Script", "getScript", args=(script_id,), env=getenv(self)).webCall(self)
    
    def post(self, action):
        if action == "add":
            OpenAPI("db", "Script", "saveScript", args=(self.get_argument("name"), "owner", self.get_argument("content")), env=getenv(self)).webCall(self)
        if action == "runScript":
            OpenAPI("openapi", None, "runScript", args=(self.get_argument("script_id"), self.get_argument("host_id")), env=getenv(self)).webCall(self)
    
    def put(self, script_id):
        OpenAPI("db", "Script", "updateScript", args=(script_id, self.get_argument("content")), env=getenv(self)).webCall(self) 

class Host(tornado.web.RequestHandler):
    def get(self, host_id):
        if host_id == "showall":
            OpenAPI("db", "Host", "getAllHosts", args=(), env=getenv(self)).webCall(self) 
        else:
            OpenAPI("db", "Host", "getHost", args=(host_id,), env=getenv(self)).webCall(self)
    
    def post(self, action):
        OpenAPI("db", "Host", "saveHost", args=(self.get_argument("name"), 
                                                self.get_argument("ip"), 
                                                self.get_argument("ssh_port"),
                                                self.get_argument("type")), env=getenv(self)).webCall(self)
    
    def put(self, host_id):
        OpenAPI("db", "Host", "updateHost", args=(host_id, 
                                                self.get_argument("name"), 
                                                self.get_argument("ssh_port"),
                                                self.get_argument("type")), env=getenv(self)).webCall(self) 


class Server(tornado.web.RequestHandler):
    def get(self, server_id):
        if server_id == "showall":
            OpenAPI("db", "Server", "getAllServers", args=(), env=getenv(self)).webCall(self) 
        else:
            OpenAPI("db", "Server", "getServer", args=(server_id,), env=getenv(self)).webCall(self)
  
    def post(self, action):
        OpenAPI("db", "Server", "saveServer", args=(self.get_argument("name"), self.get_argument("host"), 
                                                    self.get_argument("ssh_port"),self.get_argument("type"),
                                                    self.get_argument("port"),self.get_argument("webapp_home")), 
                env=getenv(self)).webCall(self)
                
    def put(self, server_id):
        OpenAPI("db", "Server", "updateServer", args=(server_id, self.get_argument("name"), self.get_argument("host"), 
                                                    self.get_argument("ssh_port"),self.get_argument("type"),
                                                    self.get_argument("port"),self.get_argument("webapp_home")), 
                env=getenv(self)).webCall(self)

class Job(tornado.web.RequestHandler):
    def get(self, job_id):
        OpenAPI("db", "Job", "getJob", args=(job_id,), env=getenv(self)).webCall(self)
    
    def post(self, action):
        OpenAPI("db", "Job", "saveJob", args=(self.get_argument("data"),), env=getenv(self)).webCall(self)
    
    def put(self, job_id):
        OpenAPI("db", "Job", "updateJob", args=(job_id, self.get_argument("data"),), env=getenv(self)).webCall(self) 

class App(tornado.web.RequestHandler):
    def get(self, app_id):
        if app_id == "showall":
            OpenAPI("db", "App", "getAllApps", args=(), env=getenv(self)).webCall(self)      
        else:
            OpenAPI("db", "App", "getApp", args=(app_id,), env=getenv(self)).webCall(self)
    
    def post(self, action):
        OpenAPI("db", "App", "saveApp", args=(self.get_argument("brand").upper(),self.get_argument("app").upper(),
                                              {"MASTER_SVN": self.get_argument("master_svn"), "CONFIG_SVN": self.get_argument("config_svn"),
                                               "CONTEXT": self.get_argument("context"), "SERVERS": self.get_argument("servers"), 
                                               "CDN_TYPE": self.get_argument("cdn_type"),"DOMAINID":self.get_argument("domainId"), "URL":self.get_argument("url")}), 
                env=getenv(self)).webCall(self)

    def put(self, app_id):
        OpenAPI("db", "App", "updateApp", args=(self.get_argument("id"),
                                              {"MASTER_SVN": self.get_argument("master_svn"), "CONFIG_SVN": self.get_argument("config_svn"),
                                               "CONTEXT": self.get_argument("context"), "SERVERS": self.get_argument("servers"),
                                               "CDN_TYPE": self.get_argument("cdn_type"),"DOMAINID":self.get_argument("domainId"), "URL":self.get_argument("url")},), env=getenv(self)).webCall(self) 

class RunAppPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/runApp.html')

class NewJobPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/newJob.html')

class OpenApiExecHistPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/openApi_exec_hist.html')

class AppDeployHistPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/app_deploy_hist.html')

class ScriptPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/script.html')

class ServerPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/server.html')
        
class HostPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/host.html')
        
class AppPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/app.html')
       
class JobPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/job.html')

class TestPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/test.html')
               
class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        class_name = self.get_argument("kw")
        startdate = self.get_argument("startdate", default=None)
        enddate = self.get_argument("enddate", default=None)
        search_type = self.get_argument("type")
        cls = utils.getClass("db", class_name)
        between_method = getattr(getattr(cls, "createtime", "default"), "between", "default")
        #检查createtime是否存在
        if between_method == "default" or startdate == None or enddate == None:
            objs = getattr(cls, "select")()
        else:
            objs = getattr(cls, "select")().where(between_method(startdate, enddate))
            
        if search_type == "selector":
            self.write(self.render_string("html/template/" + class_name.lower() + ".selector.template", objs=[obj for obj in objs]))
        else:
            self.write(self.render_string("html/template/" + class_name.lower() + "list.template", objs=[obj for obj in objs]))

class SocketHandler(tornado.websocket.WebSocketHandler):
    terminals = set()
    
    def on_message(self, message):        
        '''    if data["action"] == "packApp":
            openapi.packApp(data["buildxml"], data["version"], self)
            return
        
        if data["action"] == "deployApp":
            openapi.deployApp(data["brand"], data["app"], self)
            return
        '''    
        def deployApp(data, self):
            env = utils.Namespace()
            setattr(env, "machine", "")
            setattr(env, "ipaddr", self.request.remote_ip)
            setattr(env, "username", "")
            setattr(env, "program", "webctl") 
            master_svn = data.get("master_svn")
            config_svn = data.get("config_svn")
            logging.debug("master_svn:" + str(master_svn))
            logging.debug("config_svn:" + str(config_svn))
            
            if not master_svn:
                master_svn = "HEAD"
            if not config_svn:
                config_svn = "HEAD"         
            
            OpenAPI("openapi", None, "deployApp",
                args=(data.get("brand").upper(), data.get("app").upper(), 
                      master_svn, config_svn),env=env).socketCall(self)
           
        def packApp(data, self):
            command.packApp(data.get("buildxml"), data.get("version"), self)
            
        def stopServer(data, self):
            env = utils.Namespace()
            setattr(env, "machine", "")
            setattr(env, "ipaddr", self.request.remote_ip)
            setattr(env, "username", "")
            setattr(env, "program", "webctl") 
            OpenAPI("openapi", None, "stopServer", args=(data.get("brand"), data.get("res")), env=getenv(self)).socketCall(self, 600)
            
        def startServer(data, self):
            env = utils.Namespace()
            setattr(env, "machine", "")
            setattr(env, "ipaddr", self.request.remote_ip)
            setattr(env, "username", "")
            setattr(env, "program", "webctl") 
            OpenAPI("openapi", None, "startServer", args=(data.get("brand"), data.get("res")), env=getenv(self)).socketCall(self, 600)
        
        def restartServer(data, self):
            env = utils.Namespace()
            setattr(env, "machine", "")
            setattr(env, "ipaddr", self.request.remote_ip)
            setattr(env, "username", "")
            setattr(env, "program", "webctl") 
            OpenAPI("openapi", None, "restartServer", args=(data.get("brand"), data.get("res")), env=getenv(self)).socketCall(self, 600)
           
        action = {
                  'deployApp':deployApp,
                  'standard-deploy':deployApp,
                  'packApp':packApp,
                  'stopServer':stopServer,
                  'startServer':startServer,
                  'restartServer':restartServer
                  }
        def f(data, self):
            action.get(data.get("action"))(data, self)
        logging.debug(message)
        f(json.loads(message)["data"], self)
    
    def open(self, *args, **kwargs):
        tornado.websocket.WebSocketHandler.open(self, *args, **kwargs)
        SocketHandler.terminals.add(self)
        
        
    def on_close(self):
        tornado.websocket.WebSocketHandler.on_close(self)
        logging.debug("on_close")
        SocketHandler.terminals.remove(self)
        
    def check_origin(self, origin):
        return True
    
def make_app():
    context = env.config.get("WEB_CONTEXT")
    return tornado.web.Application([
        (context + r"/mem/flush/(\w+)/(\w+)", flushmem),
        (context + r"/mem/keys/(\w+)/(\w+)", keysmem),
        (context + r"/app/info/(\w+)/(\w+)", infoapp),
        (context + r"/svn/log/(\w+)/(\w+)", getSVNLog),
        (context + r"/script/(\w+)", Script),
        (context + r"/server/(\w+)", Server),
        (context + r"/job/(\w+)", Job),
        (context + r"/app/(\w+)", App),
        (context + r"/host/(\w+)", Host),
        
        (context + r"/", RunAppPageHandler),
        (context + r"/runApp", RunAppPageHandler),
        (context + r"/newJob", NewJobPageHandler),
        (context + r"/openApi_exec_hist", OpenApiExecHistPageHandler),
        (context + r"/app_deploy_hist", AppDeployHistPageHandler),
        (context + r"/script", ScriptPageHandler),
        (context + r"/app", AppPageHandler),
        (context + r"/server", ServerPageHandler),
        (context + r"/host", HostPageHandler),
        (context + r"/job", JobPageHandler),
        (context + r"/test", TestPageHandler),
        (context + r"/search", SearchHandler),
        (context + r"/soc", SocketHandler),
        
        (context + r"/static/index.html", tornado.web.RedirectHandler, {"url":"/fanctl/runApp"}),
        (context + r"/css/(.*)", tornado.web.StaticFileHandler, {"path": "html/css"}),
        (context + r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "html/js"}),
        (context + r"/img/(.*)", tornado.web.StaticFileHandler, {"path": "html/img"}),
        (context + r"/images/(.*)", tornado.web.StaticFileHandler, {"path": "html/images"}),
        (context + r"/font/(.*)", tornado.web.StaticFileHandler, {"path": "html/font"}),
        (context + r"/conf/(.*)", tornado.web.StaticFileHandler, {"path": "bin/conf"}),
    ])

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
    config = env.configure("conf.ini")
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
