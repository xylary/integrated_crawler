# -*- coding: utf-8 -*-

import os, re
import time, datetime
import requests
import lxml, bs4
import logging
import csv
import sqlite3 as sql
import ssl
from .selenium_webdriver import *
from .zhima_proxy import *
import pandas as pd


ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL_TO_NEXT_PAGE = 2.0
TIME_INTERVAL_TO_NEXT_CITY = 2.0
TIME_INTERVAL_RETRY = 2.0

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}

PROXY = ''

verify_counter = 0
block_counter = 0


def change_proxy():
    global PROXY
    ip = get_ip_proxy_from_zhimadaili(num=1, target_url='https://www.dianping.com')[0]
    if PROXY != '':
        print(requests.get(url_to_del_whitelist + PROXY.split(':')[0]).text)
        time.sleep(2.0)
    print(requests.get(url_to_set_whitelist + ip.split(':')[0]).text)
    PROXY = ip
    print('Reset new proxy as: ' + PROXY)
    return


def request_dianping_url(url, method='GET', max_retries=3, **kwargs):
    counter = 0
    global PROXY, verify_counter, block_counter
    while True:
        if PROXY == '':
            change_proxy()

        proxies = {
            'http': 'http://' + PROXY,
            'https': 'https://' + PROXY
        }

        ProxyError_counter = 0
        while True:
            try:
                response = requests.request(method, url=url, headers=headers, proxies=proxies, timeout=20)
                break
            except Exception as e:
                logging.error(e)
                print(type(e))
                print(e)
                if isinstance(e, requests.exceptions.ProxyError):
                    ProxyError_counter += 1
                if ProxyError_counter > 3:
                    change_proxy()
                    ProxyError_counter = 0

        verify_counter += 1
        block_counter += 1

        if response.status_code == 200:
            print(str(response.status_code) + ': ' + url)
            h = bs4.BeautifulSoup(response.content, 'lxml')
            if h.find('title').text == '验证中心':
                with open('dev/verify.html', 'w+', encoding='UTF-8', newline='') as html_file:
                    html_file.write(str(h.prettify()))
                print('需要验证, times of requests before verification is needed = ' + str(verify_counter))
                logging.error('R-counter = {} when verification is needed.'.format(str(verify_counter)))
                print(url)
                print(proxies['https'])
                '''
                b = init_browser(url + 'up=' + PROXY, proxy='127.0.0.1:8080')
                b.implicitly_wait(5)
                while True:
                    try:
                        handles = b.window_handles
                        time.sleep(0.5)
                    except:
                        verify_counter = 0
                        break
                '''
                change_proxy()
            else:
                break
        else:
            print('Status Code = ', response.status_code)
            print('Retrying to fetch transactions...')
            counter += 1
            if counter >= max_retries:
                print('Retries over {} times, program exit.'.format(str(max_retries)))
                print('Times of requests before IP is blocked = ', block_counter)
                logging.error('R-counter = {} when ip is blocked.'.format(block_counter))
                logging.error('End url = ' + url)
                change_proxy()
                block_counter = 0
                counter = 0
            time.sleep(TIME_INTERVAL_RETRY)

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
                time.sleep(TIME_INTERVAL_TO_NEXT_CITY)
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
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + '/p' + str(cur_page)
            else:
                url = url.replace('/p'+str(cur_page-1), '/p'+str(cur_page))
            r = requests.get(url, headers=headers)
            h = bs4.BeautifulSoup(r.content, 'lxml')
    return


def search_restaurant_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/10_{}'.format(str(city_id), keywords)
    h = request_dianping_url(url)
    detail_csvfile = 'dianping_results/' + 'restaurant_details_' + keywords + '.csv'
    total_number = 0
    if h.find('div', class_='page') is None:
        total_pages = 1
    else:
        total_pages = int(h.find('div', class_='page').find_all('a')[-2].attrs['data-ga-page'])
    cur_page = 1
    while True:
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
        if cur_page <= total_pages:
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + '/p' + str(cur_page)
            else:
                url = url.replace('/p' + str(cur_page - 1), '/p' + str(cur_page))
            h = request_dianping_url(url)
        else:
            print('Found {} restaurant in city_id: {}.'.format(str(total_number), str(city_id)))
            return total_number


def start_crawler(keyword, city_id_list, start_city_id):
    for city_id in city_id_list:
        if city_id >= start_city_id:
            total_number_in_city = search_restaurant_in_city(keyword, city_id)
            print('Total results in city: {}  == {}.'.format(str(city_id), str(total_number_in_city)))
            time.sleep(2.0)
    print(requests.get(url_to_del_whitelist + PROXY.split(':')[0]).text)


def search_keyword_in_dianping(keyword, start_city_id=1):
    # If using baidu map source:
    # bdmap_result_csvfile = 'data/baidumap_results/{}_20190220.csv'.format(keyword)
    df_nierson = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
    city_id_list = sorted(list(df_nierson.meituan_city_id))
    start_crawler(keyword, city_id_list, start_city_id)
    print('Finished crawling info of: ', keyword)


def clean_csv_results(csvfilename):
    df = pd.read_csv(csvfilename, names=['city_id', 'keyword', 'dianping_shop_id', 'shop_title', 'stars', 'shop_url', 'state'])
    df = df.drop_duplicates(keep='first')
    df.to_csv(csvfilename.replace('.csv', '_cleaned.csv'))
    print('Finished cleaning file: ' + csvfilename)
