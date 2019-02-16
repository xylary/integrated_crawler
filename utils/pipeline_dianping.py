import os, re
import time, datetime
import requests
import lxml, bs4
import logging
import js2py, execjs
import csv
import sqlite3 as sql
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")


TIME_INTERVAL = 3
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'Cookie': '_lxsdk_cuid=168f43fde8fc8-02873e5fbb55ab-1333063-4b9600-168f43fde90c8; _lxsdk=168f43fde8fc8-02873e5fbb55ab-1333063-4b9600-168f43fde90c8; _hc.v=562e7bde-49a0-b88e-f02c-938dcdb43337.1550286053; s_ViewType=10; cy=1; cye=shanghai; _lxsdk_s=168f506de31-4ac-c5c-37%7C%7C183'
}

'''
proxies = {
    'https://www.dianping.com': 'http://10.10.1.10:5323'
}
'''


def request_dianping_url(url, method='GET', max_retries=5, **kwargs):
    counter = 0
    while True:
        response = requests.request(method, url=url, headers=headers)
        if response.status_code == 200:
            print(str(response.status_code) + ': ' + url)
            h = bs4.BeautifulSoup(response.content, 'lxml')
            if h.find('title').text == '验证中心':
                print('需要验证： url = ', url)
                input('请在完成验证后输入任意键继续：')
            else:
                break
        else:
            print('Status Code = ', response.status_code)
            print('Retrying to fetch transactions...')
            print(response.text)
            counter += 1
            if counter > max_retries:
                print('Retries over {} times, program exit.'.format(str(max_retries)))
                exit(1)
            time.sleep(TIME_INTERVAL * 1.5)

    return h


def get_city_id(csvfilename):
    city_ids = dict()
    url = 'http://www.dianping.com/citylist'
    h = request_dianping_url(url, 'GET')
    groups = h.find_all('li', class_='letter-item')
    with open(csvfilename, 'w+', encoding='UTF-8', newline='') as csvfile:
        csvfile.write('city_name,city_url,city_id\n')
        for group in groups:
            print('Now finding cities whose first-letter = ' + group.find('div', class_='oneletter').text)
            city_links = group.find_all('a')
            for city_link in city_links:
                city = city_link.text
                city_url = 'http:' + city_link.attrs['href'] + '/'
                h = request_dianping_url(city_url, 'GET')
                start_point = str(h).find("'cityId'")
                end_point = str(h).find(",  // 城市id")
                city_id = str(h)[start_point + 11:end_point - 1]
                csvfile.write(city + ',' + city_url + ',' + city_id + '\n')
                time.sleep(TIME_INTERVAL / 3)
    return city_ids


def search_store_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/0_{}'.format(str(city_id), keywords)
    print(url)
    r = requests.get(url, headers=headers)
    h = bs4.BeautifulSoup(r.content, 'lxml')
    total_number_string = h.find('div', class_='bread J_bread').find_all('span')[-1].text
    start_point = total_number_string.find('找到') + 2
    end_point = total_number_string.find('个')
    total_number = int(total_number_string[start_point:end_point])
    if total_number > 0:
        if h.find('div', class_='page') is None:
            total_pages = 1
        else:
            total_pages = int(h.find('div', class_='page').find_all('a')[-2].attrs['data-ga-page'])
        cur_page = 1
        while cur_page <= total_pages:
            lis = h.find('div', {'id': 'shop-all-list'}).find_all('li')
            for li in lis:
                store_title = li.find('div', class_='tit').find('a').attrs['title']
                store_id = li.find('div', class_='tit').find('a').attrs['data-shopid']
                store_score = li.find('div', class_='comment').find('span').attrs['title']
                store_comment_url = li.find('div', class_='comment').find('a').attrs['href']
                print(store_id, store_title, store_score, store_comment_url)
            cur_page += 1
            time.sleep(2.0)
            if cur_page == 2:
                url = url + '/p' + str(cur_page)
            else:
                url = url.replace('/p'+str(cur_page-1), '/p'+str(cur_page))
            r = requests.get(url, headers=headers)
            h = bs4.BeautifulSoup(r.content, 'lxml')
    return


def search_restaurant_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/10_{}'.format(str(city_id), keywords)
    h = request_dianping_url(url, 'GET')
    print(h.find('title').text)
    detail_csvfile = 'dianping_results/' + 'restaurant_details_' + keywords + '.csv'
    total_number = 0
    if h.find('div', class_='page') is None:
        total_pages = 1
    else:
        total_pages = int(h.find('div', class_='page').find_all('a')[-2].attrs['data-ga-page'])
    cur_page = 1
    while cur_page <= total_pages:
        not_found_div = h.find('div', class_='not-found')
        if not_found_div is None:
            shoplist = h.find('div', {'id': 'shop-all-list'})
            if shoplist is not None:
                lis = shoplist.find_all('li')
                total_number += len(lis)
                with open(detail_csvfile, 'a+', encoding='UTF-8', newline='') as f:
                    for li in lis:
                        store_title = li.find('div', class_='tit').find('a').attrs['title']
                        store_id = li.find('div', class_='tit').find('a').attrs['data-shopid']
                        store_score = li.find('div', class_='comment').find('span').attrs['title']
                        store_comment_url = li.find('div', class_='comment').find('a').attrs['href']
                        store_status = li.find('span', class_='istopTrade')
                        if store_status is None:
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',\n'
                        elif store_status.text != '歇业/关闭':
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',歇业/关闭\n'
                        else:
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',' + store_status.text + '\n'
                        f.write(line)
        else:
            print('Found {} restaurant in city_id: {}.'.format(str(0), str(city_id)))
            return total_number
        cur_page += 1
        time.sleep(3.0)
        if cur_page == 2:
            url = url + '/p' + str(cur_page)
        else:
            url = url.replace('/p' + str(cur_page - 1), '/p' + str(cur_page))
        h = request_dianping_url(url, 'GET')
        print(h.find('title').text)
    print('Found {} restaurant in city_id: {}.'.format(str(total_number), str(city_id)))
    return total_number

