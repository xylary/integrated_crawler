# -*- coding: utf-8 -*-

import os, re
import time, datetime
import csv
import sqlite3 as sql
import ssl
import pandas as pd
from utils.general_request import *


logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL_TO_NEXT_PAGE = 2.0
TIME_INTERVAL_TO_NEXT_CITY = 2.0


def get_city_id(csvfilename):
    city_ids = dict()
    url = 'http://www.dianping.com/citylist'
    h = request_url(url, 'GET')
    groups = h.find_all('li', class_='letter-item')
    with open(csvfilename, 'w+', encoding='UTF-8', newline='') as csvfile:
        csvfile.write('city_name,city_url,city_id\n')
        for group in groups:
            print('Now finding cities whose first-letter = ' + group.find('div', class_='oneletter').text)
            city_links = group.find_all('a')
            for city_link in city_links:
                city = city_link.text
                city_url = 'http:' + city_link.attrs['href'] + '/'
                h = request_url(city_url, 'GET')
                start_point = str(h).find("'cityId'")
                end_point = str(h).find(",  // 城市id")
                city_id = str(h)[start_point + 11:end_point - 1]
                csvfile.write(city + ',' + city_url + ',' + city_id + '\n')
                time.sleep(TIME_INTERVAL_TO_NEXT_CITY)
    return city_ids


def search_restaurant_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/10_{}'.format(str(city_id), keywords)
    h = request_url(url)
    detail_csvfile = 'dianping_results/raw/' + 'restaurant_details_' + keywords + '.csv'
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
            h = request_url(url)
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
    df_nierson = pd.read_csv('data/dianping_results/nierson_city_list.csv', encoding='gbk')
    city_id_list = sorted(list(df_nierson.meituan_city_id))
    start_crawler(keyword, city_id_list, start_city_id)
    print('Finished crawling info of: ', keyword)


def clean_csv_results(csvfilename):
    try:
        df = pd.read_csv(csvfilename,
                         names=['city_id', 'keyword', 'dianping_shop_id', 'shop_title', 'stars', 'shop_url', 'state'],
                         encoding='UTF-8')
    except UnicodeDecodeError as e1:
        df = pd.read_csv(csvfilename,
                         names=['city_id', 'keyword', 'dianping_shop_id', 'shop_title', 'stars', 'shop_url', 'state'],
                         encoding='gbk')
    except Exception as e2:
        print('Exception found when cleaning: ', csvfilename)
        print(e2)
        return
    finally:
        df = df.drop_duplicates(keep='first')
        new_name = csvfilename.replace('raw', 'cleaned')
        df.to_csv(new_name, encoding='utf-8')
        print('Finished cleaning file: ' + csvfilename)


def clean_data(path='data/dianping_results/raw/'):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name not in ['dianping_city_list.csv', 'nierson_city_list.csv']:
                clean_csv_results(path + name)
    print('Finished cleaning data.')


def merge_cleaned_data(folder_path='dianping_results/cleaned/'):
    dfs = []
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            df = pd.read_csv(folder_path + name, encoding='gbk')
            dfs.append(df)
    df = pd.concat(dfs)
    df.to_csv('dianping_cleaned_in_one.csv', encoding='gbk')
