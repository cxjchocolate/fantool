# coding=gbk
'''
Created on 2016��1��15��

@author: ����
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