# -*- coding: utf-8 -*-

import requests
import logging
logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

pack = 40740
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}

def get_ip_proxy_from_zhimadaili(num=1, target_url=None):

    zhima_url = 'http://webapi.http.zhimacangku.com/getip'
    global pack
    params = {
        'num': num,           # 获取IP数量
        'type': 2,          # 数据格式：1:TXT 2:JSON 3:html
        'pro': 0,           # 省份，默认全国
        'city': 0,          # 城市，默认全国
        'regions': '',      # 全国混拨地区
        'yys': 0,           # 运营商: 0:不限 100026:联通 100017:电信
        'port': 11,         # IP协议: 1:HTTP 2:SOCK5 11:HTTPS
        'pack': pack,      # 用户套餐ID
        'ts': 1,            # 显示IP过期时间: 1:显示 2:不显示
        'ys': 0,            # 显示IP运营商: 1:显示 2:不显示
        'cs': 0,            # 显示IP位置: 1:显示 2:不显示
        'lb': 1,            # 分隔符(1:\r\n 2:/br 3:\r 4:\n 5:\t 6 :自定义)
        'sb': 0,
        'pb': 4,            # 端口位数（4:4位端口 5:5位端口）
        'mr': 1,            # 去重选择（1:360天去重 2:单日去重 3:不去重）
    }
    counter = 0
    while counter <= 5:
        r = requests.get(zhima_url, params=params)
        c = r.json()
        if c['success']:
            proxy = c['data'][0]['ip'] + ':' + str(c['data'][0]['port'])
            expire_time = c['data'][0]['expire_time']
            proxies = {
                'http': 'http://' + proxy,
                'https': 'https://' + proxy
            }
            if target_url is None:
                target_url = 'http://www.baidu.com'
            try:
                r = requests.get(target_url, headers=headers, proxies=proxies, timeout=5)
                if r.status_code == 200:
                    return (proxy, expire_time)
            except Exception as e:
                logging.error(e)
        else:
            print(r.text)
        counter += 1
    print('Cannot get useful proxy, please check the source')
    exit(1)
