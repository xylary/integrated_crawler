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


r = requests.request('GET', url, headers=headers, proxies=proxy)
print(r.status_code)
'''

test_url = 'https://www.dianping.com'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'If-None-Match': 'W/"55d64ed40c5bf08bb94edce6bffa8732"'
}


def get_proxies(source_url='https://www.xicidaili.com/nn/'):
    for i in range(500, 1000):
        if i % 5 == 0:
            print('Testing proxies on page: ' + str(i))
        r = requests.get(source_url + '1', headers=headers)
        if r.status_code == 200:
            with open('temp.txt', 'w+', encoding='UTF-8', newline='') as f:
                f.write(r.text)
            text = ''
            with open('temp.txt', 'r+', encoding='UTF-8', newline='') as f:
                lines = f.readlines()
            for line in lines:
                text += line
            h = bs4.BeautifulSoup(text, 'lxml')
            rows = h.find('table', {'id': 'ip_list'}).find_all('tr')[1:]
            for row in rows:
                host = row.find_all('td')[1].text
                port = row.find_all('td')[2].text
                proxy = {
                    'http': 'http://' + host + ':' + port,
                    'https': 'http://' + host + ':' + port
                }
                try:
                    r = requests.get(test_url, headers=headers, proxies=proxy, timeout=5)
                    with open('proxies_available.csv', 'a+', encoding='UTF-8', newline='') as f:
                        f.write(host + ',' + port + '\n')
                    print('Testing: ' + host + ':' + port + ', succeeded and saved')
                except Exception as e:
                    print(e)
                    print('Testing: ' + host + ':' + port + ', failed and discard')
        time.sleep(0.5)
    return


get_proxies()
