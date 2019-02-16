import os, re
import time, datetime
import requests
import lxml, bs4
import logging
import js2py, execjs
import csv
import sqlite3 as sql

'''
proxy = {
    'http': 'http://111.177.167.67:9999',
    'https': 'http://111.177.167.67:9999'
}

url = 'http://www.baidu.com'
r = requests.request('GET', url, headers=headers, proxies=proxy)
print(r.status_code)
'''

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'If-None-Match': 'W/"55d64ed40c5bf08bb94edce6bffa8732"'
}

def get_proxies(source_url='https://www.xicidaili.com/nn/'):
    proxies = []
    r = requests.get(source_url + '1', headers=headers)
    if r.status_code == 200:
        h = bs4.BeautifulSoup(r.content, 'lxml', exclude_encodings='UTF-8')
        print(h.prettify())
        rows = h.find('div', {'id': 'ip_list'}).find_all('tr')[1:]
        for row in rows:
            host = row.find_all('td')[1].text
            port = row.find_all('td')[2].text
            print(host + ':' + port)
            proxies.append(host + ':' + port)
    return proxies


get_proxies()
