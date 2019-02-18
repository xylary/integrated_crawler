#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
import time, datetime
import requests
import lxml, bs4
import logging
import js2py, execjs
import csv
import sqlite3 as sql


url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=%E6%B2%99%E6%8B%89%E6%96%AF&c=1&src=0&wd2=&pn=0&sug=0&l=5&b=(7797075.220000001,1032027.8800000008;15415635.22,8306523.880000001)&from=webmap&biz_forward={%22scaler%22:1,%22styles%22:%22pl%22}&sug_forward=&auth=b0fJUR7RJ15JIXGVf1yYUJbKY8gBU6NQuxHHVERNBBLtComRB199Ay1uVt1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3GuEtXzljPaVjyBDEHKOQUWYxcEWe1GD8zv7u%40ZPuVteuEthjzgjyBKKYHUQYDOxjnOOA5zhBaIWKvADJzEjjg2K&device_ratio=1&tn=B_NORMAL_MAP&nn=0&u_loc=13520671,3640234&ie=utf-8&t=1550487372309'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'cookie': 'BAIDUID=8E005E4C2202079D49172CBF6BEF0330:FG=1; BIDUPSID=8E005E4C2202079D49172CBF6BEF0330; PSTM=1549872758; delPer=0; PSINO=7; ZD_ENTRY=empty; H_PS_PSSID=26522_1455_21117_26350_28413_27543; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; MCITY=-%3A',
    'Referer': 'https://map.baidu.com/?wd=%E6%B2%99%E6%8B%89%E6%96%AF'

}

# url = url.replace('{}', '味千拉面')

r = requests.get(url, headers=headers)
print(r.status_code)
results = r.json()
for hot_city in results['hot_city']:
    city_name = hot_city.split('|')[0]
    city_num = hot_city.split('|')[1]
    print(city_name, ': ', city_num)
'''
for province in results['more_city']:
    print(province['province_id'], province['province'], province['num'])
    for city in province['city']:
        print('--', city['code'], '-', city['name'], ': ', city['num'])
'''

c = r.json()
print(c)



'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=沙拉斯&c=1&src=0&wd2=&pn=0&sug=0&l=5&b=(2533801.9599782247,-822699.24999044;20646313.959978223,9802324.75000956)&from=webmap&biz_forward={%22scaler%22:1,%22styles%22:%22pl%22}&sug_forward=&auth=QJZFI%3DIHCc38HB1x7IXDbExF8E9veD45uxHHVBBBBTVtBnlQADZZz1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3Guzt7xjhN%40ThwzBDGJ4P6VWvlEeLZNz1VD%3DCUbB1A8zv7u%40ZPuVteuVtegvcguxHHVBBBBLLtjnOOAJzvaaZyB&device_ratio=1&tn=B_NORMAL_MAP&nn=0&ie=utf-8&t=1550333392415'