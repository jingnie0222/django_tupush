#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'zhangjingjun'
__mtime__ = '2018/3/29'
# ----------Dragon be here!----------
              ┏━┓      ┏━┓
            ┏━┛ ┻━━━━━━┛ ┻━━┓
            ┃       ━       ┃
            ┃  ━┳━┛   ┗━┳━  ┃
            ┃       ┻       ┃
            ┗━━━┓      ┏━━━━┛
                ┃      ┃神兽保佑
                ┃      ┃永无BUG！
                ┃      ┗━━━━━━━━━┓
                ┃                ┣━┓
                ┃                ┏━┛
                ┗━━┓ ┓ ┏━━━┳━┓ ┏━┛
                   ┃ ┫ ┫   ┃ ┫ ┫
                   ┗━┻━┛   ┗━┻━┛
"""
from django import template
from django.utils.safestring import mark_safe
register = template.Library()
import requests
import html

@register.simple_tag
def formatTime(intime):
    return intime.strftime("%m%d %H:%M")

@register.simple_tag
def formatIp(inip):
    ip = 'http://10.153.51.60:12000/xml'
    ip_list = inip.split('/')
    # print(ip_list)
    return ip_list[2]

@register.simple_tag
def formatStr(htmlStr):
    s =html.unescape(htmlStr)
    s = s.replace('nowrap="nowrap"','')
    with open('diff.html','w',encoding='utf-8') as fw:
        fw.write(htmlStr)
    # print(s)
    return s

@register.simple_tag
def getRate(finishNum,diffNum):
    result=0
    if finishNum!=0:
        result = round(float(diffNum)/float(finishNum)*100,2)
    return result


if __name__ == '__main__':
    pass