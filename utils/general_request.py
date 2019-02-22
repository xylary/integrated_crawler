# -*- coding: utf-8 -*-

import bs4
import logging
import ssl
from proxies.zhima_proxy import *


ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}

PROXY = ''
counter_verification = 0
counter_block = 0
TIME_INTERVAL_RETRY = 2.0


def change_proxy(test_url=None):
    global PROXY
    ip = get_ip_proxy_from_zhimadaili(num=1, test_url=test_url)[0]
    if PROXY != '':
        print(requests.get(url_to_del_whitelist + PROXY.split(':')[0]).text)
        time.sleep(2.0)
    print(requests.get(url_to_set_whitelist + ip.split(':')[0]).text)
    PROXY = ip
    print('Reset new proxy as: ' + PROXY)
    return


def require_verification(bs4_html):
    return bs4_html.find('title').text == '验证中心'


def request_url(url, method='GET', max_retries=3, **kwargs):
    counter_retry = 0
    global PROXY, counter_verification, counter_block
    while True:
        if PROXY == '':
            change_proxy()
        proxies = {'http': 'http://' + PROXY, 'https': 'https://' + PROXY}

        counter_proxy_error = 0
        while True:
            try:
                response = requests.request(method, url=url, headers=headers, proxies=proxies, timeout=20)
                break
            except Exception as e:
                print(e)
                if isinstance(e, requests.exceptions.ProxyError):
                    print('Wait 10 seconds and then retry...')
                    counter_proxy_error += 1
                    time.sleep(10)
                if counter_proxy_error >= 5:
                    change_proxy()
                    counter_proxy_error = 0

        counter_verification += 1
        counter_block += 1

        if response.status_code != 200:
            print('Status Code = ', response.status_code)
            print('Retrying to fetch transactions...')
            counter_retry += 1
            if counter_retry >= max_retries:
                msg = 'IP blocked, requests made before IP is blocked = ' + str(counter_block) + '\n'
                msg += 'End url: ' + url
                print(msg)
                logging.error(msg)
                change_proxy()
                counter_block = 0
                counter_retry = 0
            time.sleep(TIME_INTERVAL_RETRY)

        else:
            print(str(response.status_code) + ': ' + url)
            h = bs4.BeautifulSoup(response.content, 'lxml')
            if require_verification(h):
                msg = '需要验证, times of requests before verification is needed = ' + str(counter_verification) + '\n'
                msg += 'url: ' + url + ' , proxy: ' + PROXY
                logging.error(msg)
                print(msg)
                change_proxy()
                counter_verification = 0
            else:
                return h
