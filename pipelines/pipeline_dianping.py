# -*- coding: utf-8 -*-

import os, re
import time, datetime
import csv
import sqlite3 as sql
import ssl
import json
import pandas as pd
from utils.general_request import *


logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL_TO_NEXT_PAGE = 2.0
TIME_INTERVAL_TO_NEXT_CITY = 2.0


PROVINCE_ID = {
'北京': 1,
'天津': 2,
'河北': 3,
'山西': 4,
'内蒙古': 5,
'辽宁': 6,
'吉林': 7,
'黑龙江': 8,
'上海': 9,
'江苏': 10,
'浙江': 11,
'安徽': 12,
'福建': 13,
'江西': 14,
'山东': 15,
'河南': 16,
'湖北': 17,
'湖南': 18,
'广东': 19,
'广西': 20,
'海南': 21,
'重庆': 22,
'四川': 23,
'贵州': 24,
'云南': 25,
'西藏': 26,
'陕西': 27,
'甘肃': 28,
'青海': 29,
'宁夏': 30,
'新疆': 31,
'香港': 31,
'澳门': 33,
'台湾': 34
}


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


def get_total_pages(h):
    if h.find('div', class_='page') is None:
        total_pages = 1
    else:
        total_pages = int(h.find('div', class_='page').find_all('a')[-2].attrs['data-ga-page'])
    return total_pages


def get_all_restaurants_in_results(url, to_csv, add_proxy=True):
    h = request_url(url, add_proxy=add_proxy)
    total_number = 0
    total_pages = get_total_pages(h)
    cur_page = 1
    while True:
        not_found_div = h.find('div', class_='not-found')
        if not_found_div is None:
            shoplist = h.find('div', {'id': 'shop-all-list'})
            if shoplist is not None:
                lis = shoplist.find_all('li')
                total_number += len(lis)
                with open(to_csv, 'a+', encoding='UTF-8', newline='') as f:
                    for li in lis:
                        store_title = li.find('div', class_='tit').find('a').attrs['title']
                        store_id = li.find('div', class_='tit').find('a').attrs['data-shopid']
                        store_score = li.find('div', class_='comment').find('span').attrs['title']
                        store_comment_url = li.find('div', class_='comment').find('a').attrs['href']
                        store_status = li.find('span', class_='istopTrade')
                        if store_status is None:
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',\n'
                        elif store_status.text != '歇业/关闭':
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',歇业/关闭\n'
                        else:
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',' + store_status.text + '\n'
                        f.write(line)
        else:
            print('Found {} restaurant in url: {}.'.format(str(0), url))
            return total_number

        cur_page += 1
        if cur_page <= total_pages:
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + 'p' + str(cur_page)
            else:
                url = url.replace('p' + str(cur_page - 1), 'p' + str(cur_page))
            h = request_url(url, add_proxy=add_proxy)
        else:
            print('Found {} restaurant in url: {}.'.format(str(total_number), url))
            return total_number


def search_restaurant_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/10_{}'.format(str(city_id), keywords)
    h = request_url(url)
    detail_csvfile = 'data/dianping_results/raw/' + 'restaurant_details_' + keywords + '.csv'
    total_number = 0
    total_pages = get_total_pages(h)
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


def get_category_page_urls_in_city(city_url):
    hrefs = []
    h = request_url(city_url, add_proxy=False)
    try:
        lis = h.find_all('div', class_='content city-content')[0].find_all('li')
        for li in lis:
            href = li.find('a').attrs['href']
            hrefs.append(href)
    except IndexError:
        hrefs.append(city_url)
    return hrefs


def get_all_records(city_info, channel, group):
    city = city_info['cityEnName']
    url = 'http://www.dianping.com/{}/ch{}/g{}'.format(city, str(channel), str(group))
    csvfilename = city_info['cityName'] + '_ch' + str(channel) + '_g' + str(group) + '.csv'
    hrefs = get_category_page_urls_in_city(url)
    total_records = 0
    for href in hrefs:
        total_records += get_all_restaurants_in_results(href, csvfilename, add_proxy=True)
    print('Total records in {} channel {} group {} = {}'.format(city, str(channel), str(group), str(total_records)))
    return total_records


def get_city_list(province):
    province_id = PROVINCE_ID[province]
    r = requests.post('http://www.dianping.com/ajax/citylist/getDomesticCityByProvince',
                      json={'provinceId': province_id})
    city_list = json.loads(r.content)['cityList']
    return city_list
