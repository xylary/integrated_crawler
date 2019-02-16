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


url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&' \
      'da_src=searchBox.button&wd={}&c=1&src=0&wd2=&pn=0&sug=0&l=5&' \
      'b=(2533801.9599782247,-822699.24999044;20646313.959978223,9802324.75000956)&' \
      'from=webmap&biz_forward={%22scaler%22:1,%22styles%22:%22pl%22}&sug_forward=&' \
      'auth=QJZFI%3DIHCc38HB1x7IXDbExF8E9veD45uxHHVBBBBTVtBnlQADZZz1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3Guzt7xjhN%4' \
      '0ThwzBDGJ4P6VWvlEeLZNz1VD%3DCUbB1A8zv7u%40ZPuVteuVtegvcguxHHVBBBBLLtjnOOAJzvaaZyB&' \
      'device_ratio=1&tn=B_NORMAL_MAP&nn=0&ie=utf-8&t=1550333392415'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}

url = url.replace('{}', '悦荟餐饮')

r = requests.get(url, headers=headers)
print(r.status_code)
results = r.json()
for hot_city in results['hot_city']:
    city_name = hot_city.split('|')[0]
    city_num = hot_city.split('|')[1]
    print(city_name, ': ', city_num)
for province in results['more_city']:
    print(province['province_id'], province['province'], province['num'])
    for city in province['city']:
        print('--', city['code'], '-', city['name'], ': ', city['num'])

print(r.json())
