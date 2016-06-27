# coding=gbk
'''
Created on 2015年11月5日

@author: 大雄
'''

import datetime
import json
import logging
import base64
import sys


from peewee import Model, SqliteDatabase
from peewee import TextField, DateTimeField, CharField, ForeignKeyField, IntegerField, BlobField, PrimaryKeyField
from peewee import create_model_tables
from redis import StrictRedis


config = SqliteDatabase(sys.path[0] + "/" + "db/fantool.db")
runtime = SqliteDatabase(sys.path[0] + "/" + "db/runtime.db")

class App(Model):
    id = PrimaryKeyField()
    brand = CharField(max_length=50)
    name = CharField(max_length=50)
    master_url = None
    master_rev = None
    config_url = None
    config_rev = None
    __configs = None    
    class Meta:
        db_table = 't_app'
        database = config
        
    def getConfig(self, key):
        if not self.__configs:
            self.__configs = {}
            for config in self.configs:
                self.__configs[config.key] = config.value
        return self.__configs.get(key)

    @classmethod
    def saveApp(cls, brand, name, configs):
        s1 = App()
        s1.brand = brand
        s1.name = name
        s1.save(force_insert=True)
        for (k,v) in configs.items():
            ac = AppConfig()
            ac.key = k
            ac.value = v
            ac.app = s1
            ac.save(force_insert=True)
        
        return {"id": s1.get_id()}
    
    @classmethod
    def getApp(cls, app_id):
        apps = App.select().where(App.id == app_id)
        apps = [s for s in apps]
        if len(apps) != 1:
            raise Exception("more than 1 object have been found")
        return apps[0]
    
    @classmethod
    def updateApp(cls, app_id, configs):
        o = App.getApp(app_id)
        for (k,v) in configs.items():
            logging.debug(k + ":" + v)
            logging.debug(o)
            #更新已有配置记录
            numofmodified = AppConfig.update(value = v).where(
                                                              (AppConfig.key == k) & (AppConfig.app == app_id)
                                                              ).execute()
            #如未找到配置记录，则插入
            if numofmodified == 0:
                ac = AppConfig()
                ac.key = k
                ac.value = v
                ac.app = o
                ac.save(force_insert=True)
        return None
    
    @classmethod
    def getAllApps(cls):
        apps = {}
        for app in App.select():
            if apps.get(app.brand):
                apps.get(app.brand).append(app.name)
            else:
                apps[app.brand] = [app.name]
        return apps
    
    def toJsonString(self):
        configs = {}
        for config in self.configs:
            configs[config.key] = config.value
        print(configs)
        return {
                "id":self.id, "brand":self.brand, "app":self.name, 
                "configs": configs}
            
class AppConfig(Model):
    id = PrimaryKeyField()
    key = CharField(max_length=50)
    value = CharField(max_length=50)
    app = ForeignKeyField(App, related_name='configs')
    class Meta:
        db_table = 't_app_config'
        database = config
        indexes = (
            # create a unique on from/to/date
            (('key', 'app'), True)
        )

class AppHistory(Model):
    brand = CharField(max_length=50)
    name = CharField(max_length=50)
    master_url = CharField(max_length=50, null=True)
    master_rev = CharField(max_length=10, null=True)
    config_url = CharField(max_length=50, null=True)
    config_rev = CharField(max_length=10, null=True)
    createtime = DateTimeField(default=datetime.datetime.now)
    class Meta:
        db_table = 't_app_deploy_hist'
        database = runtime

class Host(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50) 
    ip = CharField(max_length=50)
    ssh_port = IntegerField()
    type = CharField(max_length=50, null=True) 
    createtime = DateTimeField(default=datetime.datetime.now)
    lastupdate = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        db_table = 't_host'
        database = config
        
    def toJsonString(self):
        return {
                "id":self.id, "name":self.name, "ip":self.ip, 
                "ssh_port":self.ssh_port, "type":self.type, 
                "createtime":self.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                "lastupdate":self.lastupdate.strftime('%Y-%m-%d %H:%M:%S')
                }
        
    @classmethod
    def saveHost(cls, name, ip, ssh_port, host_type):
        h = Host()
        h.name = name
        h.ip = ip
        h.ssh_port = ssh_port
        h.type = host_type
        h.save(True)
        return {"id": h.get_id()}
    
    @classmethod
    def updateHost(cls, host_id, name, ip, ssh_port, host_type):
        q = Host.update(name=name, ip=ip, ssh_port=ssh_port, type=host_type, lastupdate=datetime.datetime.now()).where(Host.id == host_id)
        q.execute()
        return None
    
    @classmethod
    def getHost(cls, host_id):
        hosts = Host.select().where(Host.id == host_id)
        hosts = [s for s in hosts]
        if len(hosts) != 1:
            raise Exception("more than 1 object have been found")
        return hosts[0]
    
    @classmethod
    def getAllHosts(cls):
        hosts = Host.select()
        hosts = [s for s in hosts]
        return hosts

class Server(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50) 
    host = CharField(max_length=50)
    ssh_port = IntegerField()
    type = CharField(max_length=50) 
    port = IntegerField(default=0, null=True)
    webapp_home = CharField(max_length=100, null=True) 
    class Meta:
        db_table = 't_server'
        database = config

    @classmethod
    def getServer(cls, server_id):
        servers = Server.select().where(Server.id == server_id)
        servers = [s for s in servers]
        if len(servers) != 1:
            raise Exception("more than 1 object have been found")
        return servers[0]
    
    @classmethod
    def getAllServers(cls):
        servers = Server.select()
        servers = [s for s in servers]
        return servers
    
    @classmethod
    def saveServer(cls, name, host, ssh_port, v_type, port,webapp_home):
        s1 = Server()
        s1.name = name
        s1.host = host
        s1.ssh_port = ssh_port
        s1.type = v_type
        s1.port = port
        s1.webapp_home = webapp_home
        s1.save(force_insert=True)
        d = {}
        d["id"] = s1.get_id()
        return d

    @classmethod
    def updateServer(cls, server_id, name, host, ssh_port, v_type, port,webapp_home):
        q = Server.update(name=name, host=host, ssh_port=ssh_port, port=port, webapp_home=webapp_home).where(Server.id == server_id)
        q.execute()
        return None
    
    def toJsonString(self):
        return {
                "id":self.id, "name":self.name, "host":self.host, "ssh_port":self.ssh_port,
                "type":self.type, "port":self.port, "webapp_home":self.webapp_home
                }

class Operation(Model):
    name = CharField(max_length=50)
    createtime = DateTimeField(default=datetime.datetime.now)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    username = CharField(max_length=50, default='annoyous')
    machine = CharField(max_length=50, null=True)
    ipaddr = CharField(max_length=20, null=True)
    program = CharField(max_length=50, null=True)
    data = TextField(null=True)
    class Meta:
        db_table = 't_operation'
        database = runtime
        
    def toJsonString(self):
        return {'name': self.name, 'createtime': self.createtime, 'start_time':self.start_time,
                        'end_time':self.end_time, 'username':self.username,
                        'machine': self.machine, 'ipaddr':self.ipaddr, 'program':self.program,
                        'data':self.data}

class Script(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50,)
    createtime = DateTimeField(default=datetime.datetime.now)
    lastupdate = DateTimeField(default=datetime.datetime.now)
    owner = CharField(max_length=50, default='annoyous')
    tag = CharField(max_length=50, null=True)
    content = BlobField(null=True)
    class Meta:
        db_table = 't_script'
        database = config
        indexes = (
            (('name', 'owner'), True),
            )
    @classmethod
    def saveScript(cls, name, owner, content, tag=""):
        s1 = Script()
        s1.name = name
        s1.owner = owner
        s1.tag = tag
        s1.content = content
        s1.save(force_insert=True)
        d = {}
        d["id"] = s1.get_id()
        return d
    
    def toJsonString(self):
        return {'id':self.id, 'name': self.name, 'createtime': self.createtime, 'lastupdate':self.lastupdate,
                        'owner':self.owner, 'tag':self.tag,
                        'content': str(base64.encodebytes(self.content), "utf-8")}
    
    @classmethod
    def updateScript(cls, script_id, content):
        q = Script.update(content=content, lastupdate=datetime.datetime.now()).where(Script.id == script_id)
        q.execute()
        return None
    
    @classmethod
    def getScript(cls, script_id):
        scripts = Script.select().where(Script.id == script_id)
        scripts = [s for s in scripts]
        if len(scripts) != 1:
            raise Exception("more than 1 object have been found")
        return scripts[0]
    
    @classmethod
    def getAllScripts(cls):
        scripts = Script.select()
        scripts = [s for s in scripts]
        return scripts

class Job(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    createtime = DateTimeField(default=datetime.datetime.now)
    lastupdate = DateTimeField(default=datetime.datetime.now)
    owner = CharField(max_length=50)
    tag = CharField(max_length=50, null=True)
    desc = TextField(null=True)
    class Meta:
        db_table = 't_job_header'
        database = config
        indexes = (
            (('name', 'owner'), True),
            )
    
    def toJsonString(self):
        job_lines_json = []
        for line in self.job_lines:
            job_lines_json.append(line.toJsonString())
        return {
                "id":self.id, "name":self.name,
                "createtime":self.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                "lastupdate":self.lastupdate.strftime('%Y-%m-%d %H:%M:%S'),
                "owner":self.owner, "tag":self.tag, "desc":self.desc,
                "job_lines":job_lines_json
        }
    
    
    @classmethod
    def saveJob(cls, data):
        rawObj = json.loads(data)
        logging.debug(rawObj)
        job_name = rawObj.get("job_name")
        job = Job()
        job.name = job_name
        job.owner = "testUser"
        job.save(force_insert=True)
        
        job_lines = rawObj.get("job_lines")
        line_no = 0
        for line in job_lines:
            line_no = line_no + 1
            script_id = line.get("script_id")
            desc      = line.get("desc")
            
            job_line         = JobLine()
            job_line.script  = script_id
            job_line.desc    = desc
            job_line.line_no = line_no
            job_line.job     = job
            job_line.save(force_insert=True)
            
            detail_no = 0
            for host in line.get("job_details"):
                detail_no = detail_no + 1
                job_detail           = JobDetail()
                job_detail.host      = host.get("host_id")
                job_detail.detail_no = detail_no
                job_detail.job_line  = job_line
                job_detail.save(force_insert=True)
        return {"id":job.get_id()}
    
    @classmethod
    def getJob(cls, job_id):
        jobs = Job.select().where(Job.id == job_id)
        jobs = [j for j in jobs]
        if len(jobs) != 1:
            raise Exception("more than 1 object have been found")
        return jobs[0]
    
    @classmethod
    def updateJob(cls, job_id, data):
        pass
    
    

class JobLine(Model):
    id = PrimaryKeyField()
    createtime = DateTimeField(default=datetime.datetime.now)
    line_no = IntegerField(null=True)
    desc = TextField(null=True)
    script = ForeignKeyField(Script, related_name='relationships')
    job    = ForeignKeyField(Job,  related_name='job_lines')
    class Meta:
        db_table = 't_job_line'
        database = config
        
    def toJsonString(self):
        job_detail_json = []
        for d in self.job_details:
            job_detail_json.append(d.toJsonString())
        return {
                "id":self.id, "line_no":self.line_no, "desc":self.desc,
                "createtime":self.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                "script":{"script_id": self.script.id, "script_name":self.script.name},
                "job_details":job_detail_json  
        }
        
class JobDetail(Model):
    id = PrimaryKeyField()
    createtime = DateTimeField(default=datetime.datetime.now)
    detail_no = IntegerField(null=True)
    job_line    = ForeignKeyField(JobLine,  related_name='job_details')
    host   = ForeignKeyField(Host, related_name='relationships')
    desc = TextField(null=True)
    class Meta:
        db_table = 't_job_detail'
        database = config
        
    def toJsonString(self):
        return {
                "id":self.id, "detail_no":self.detail_no, "host":self.host.toJsonString(),
                "createtime":self.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                "desc":self.desc
        }
        
class Cache:
    cache = {}
    @classmethod    
    def invalid(cls, key):
        cls.cache.pop(key)
    
    @classmethod    
    def getCache(cls, key):
        return cls.cache.get(key)
    
    @classmethod    
    def setCache(cls, key, value):
        cls.cache[key] = value
    
    @classmethod    
    def storeCache(cls):
        # gzip json data
        pass
    
    @classmethod    
    def loadCache(cls):
        pass  

class RedisHelper():
    redis = StrictRedis(host="localhost", port='6379')  
    @staticmethod
    def flushdb(ip, port='6379'):
        return  str(StrictRedis(host=ip, port=port, db=0).flushdb())
    
    @staticmethod
    def keys(ip, port='6379'):
        strs = []
        for one in StrictRedis(host=ip, port=port, db=0).keys('*'):
            strs.append(str(one))
        return strs
    @classmethod
    def get(cls, name):
        return cls.redis.get(name)
    @classmethod
    def set(cls, name, value):
        return cls.redis.set(name, value)



if __name__ == '__main__': 
    Models = [App, AppConfig, Server, Operation, AppHistory, Script, Job, JobLine, JobDetail, Host]
     
    print("create all tables:")
    print(Models)
    create_model_tables(Models, fail_silently=True)
    print("create tables end")
    
    
