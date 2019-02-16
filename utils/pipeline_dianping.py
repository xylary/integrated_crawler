import os, re
import time, datetime
import requests
import lxml, bs4
import logging
import js2py, execjs
import csv
import sqlite3 as sql


logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")


TIME_INTERVAL = 0.25
headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
}


def get_city_id(csvfilename):
    city_ids = dict()
    url = 'http://www.dianping.com/citylist'
    r = requests.get(url, headers=headers)
    h = bs4.BeautifulSoup(r.content, 'lxml')
    groups = h.find_all('li', class_='letter-item')
    with open(csvfilename, 'w+', encoding='UTF-8', newline='') as csvfile:
        csvfile.write('city_name,city_url,city_id\n')
        for group in groups:
            print('Now finding cities whose first-letter = ' + group.find('div', class_='oneletter').text)
            city_links = group.find_all('a')
            for city_link in city_links:
                city = city_link.text
                city_url = 'http:' + city_link.attrs['href'] + '/'
                rc = requests.get(city_url, headers=headers)
                start_point = rc.text.find("'cityId'")
                end_point = rc.text.find(",  // 城市id")
                city_id = rc.text[start_point + 11:end_point - 1]
                csvfile.write(city + ',' + city_url + ',' + city_id + '\n')
                time.sleep(TIME_INTERVAL)
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


