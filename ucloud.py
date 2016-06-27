# coding=gbk
'''
Created on 2016年6月2日

@author: 大雄
'''

import hashlib
import json
import logging
import urllib.request


# class UCloudCDN(Model):
#     domainid = CharField(max_length=50)
#     domainname = CharField(max_length=50)
#     source = CharField(max_length=200)
#     class Meta:
#         db_table = 't_ucloudcdn'
#         database = config
class AbstractUCloudLib:
    PublicKey = 'ucloud13764032117@163.com14367598390001235923883'
    PrivateKey = '74516f915f8f5dc0affe2314669e5696f28347b7'
    Password = 'emFvZmFuMTIzemFvZmFu'
    HOST = "http://api.ucloud.cn"
    PORT = 80
    API = "/"
    
    @classmethod      
    def _execute(self, params):
        try:
            params["PublicKey"] = self.PublicKey
            params["Password"] = self.Password
            params["Signature"] = self._verfy_ac(params)
            encode_params = "?"
            items = sorted(params.items(), key=lambda asd:asd[0], reverse=False)
            for key, value in items:
                encode_params = encode_params + key + "=" + value + "&"
            url = self.HOST + ":" + str(self.PORT) + self.API + encode_params
            logging.debug(url)
            response = urllib.request.urlopen(url).read()
            if response:
                return json.loads(bytes.decode(response))
            else:
                return None
        except Exception as e:
            logging.debug(e)

    @classmethod
    def _verfy_ac(cls, params):
        # 请求参数串 # 将参数串排序
        items = sorted(params.items(), key=lambda asd:asd[0], reverse=False)
        params_data = "";
        for key, value in items:
            params_data = params_data + str(key) + str(value)
        params_data = params_data + cls.PrivateKey
    
        sign = hashlib.sha1()
        sign.update(str.encode(params_data))
        signature = sign.hexdigest()
        # 生成的Signature值
        return signature
    
class BasicUCloudLib(AbstractUCloudLib):
    def refreshUcdnDomainCache(self, domainId, url_type, url_list):
        params = {}
        params["Action"] = "RefreshUcdnDomainCache"
        params["DomainId"] = domainId
        params["Type"] = url_type
        params["UrlList.0"] = url_list
        return self._execute(params)
    
    def getUcdnDomainTraffic(self):
        params = {}
        params["Action"] = "GetUcdnDomainTraffic"
        return self._execute(params)
    
    def getUcdnDomainPrefetchEnable(self,domainId):
        params = {}
        params["Action"] = "GetUcdnDomainPrefetchEnable"
        params["DomainId"] = domainId
        return self._execute(params)        


   
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
    #ucloud = BasicUCloudLib()
    #result = ucloud.refreshUcdnDomainCache("ucdn-v2o1m3", "file", "http://cdn.zumuquqi.com/OrderUI/")
    #result = ucloud.getUcdnDomainTraffic()
    #result = ucloud.getUcdnDomainPrefetchEnable("ucdn-v2o1m3")
    #print(result)
    s = "{'RetCode': 0, 'Action': 'RefreshUcdnDomainCacheResponse', 'TaskId': '20160602174912_a4c99aa5'}"