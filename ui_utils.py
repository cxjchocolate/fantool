# coding=gbk
'''
Created on 2016年1月15日

@author: 大雄
'''

def beautySVNURL(url):
    if url:
        idx = url.find('/', 8)
        if idx > -1:
            return url[idx:]
        else:
            return url
    else:
        return ""