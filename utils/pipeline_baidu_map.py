#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.selenium_webdriver import *
import datetime


INIT_WAITTIME = 5
SELECT_CITY_WAIT_TIME = 2
LOADING_MAP_WAIT_TIME = 5
LOADING_INFO_WAIT_TIME = 3


def clean_data(results):
    for hot_city in results['hot_city']:
        city_name = hot_city.split('|')[0]
        city_num = hot_city.split('|')[1]
        print(city_name, ': ', city_num)
    for province in results['more_city']:
        print(province['province_id'], province['province'], province['num'])
        for city in province['city']:
            print('--', city['code'], '-', city['name'], ': ', city['num'])


def search(keyword, browser):
    browser.find_element_by_xpath('//*[@id="sole-input"]').clear()
    browser.find_element_by_xpath('//*[@id="sole-input"]').send_keys(keyword + '\n')
    time.sleep(LOADING_INFO_WAIT_TIME)
    print('The results of the keyword: {} has been saved.'.format(keyword))


def searching_keywords_on_baidumap(keywords):
    # init chromedriver
    b = init_browser('https://map.baidu.com', proxy='127.0.0.1:8080')
    time.sleep(INIT_WAITTIME)

    # enter into city, default selection = '中国'
    b.find_element_by_xpath('//*[@id="ui3_city_change"]/a').click()
    time.sleep(SELECT_CITY_WAIT_TIME)
    b.find_element_by_xpath('//*[@id="selCityHotCityId"]/a[1]').click()
    time.sleep(LOADING_MAP_WAIT_TIME)

    for keyword in keywords:
        b.find_element_by_xpath('//*[@id="sole-input"]').click()
        search(keyword, b)
        b.find_element_by_xpath('//*[@id="ui3_city_change"]/a').click()
        time.sleep(SELECT_CITY_WAIT_TIME)
        b.find_element_by_xpath('//*[@id="selCityHotCityId"]/a[1]').click()
        time.sleep(LOADING_MAP_WAIT_TIME)

    print('All search results has been saved.')
    b.quit()


def read_country_result(json_data):
    info = dict()
    try:
        info['keyword'] = json_data['place_info']['search_ext'][0]['wd']
    except Exception as e:
        print('No Keyword founded, raw data: ', json_data)
        info['keyword'] = 'NoKeyword'

    info['city_result'] = []

    if 'more_city' not in json_data.keys():
        return info

    for content in json_data['content']:
        city_info = dict()
        city_info['category'] = '热门城市'
        city_info['city_id'] = content['code']
        city_info['city_name'] = content['name']
        city_info['city_num'] = content['num']
        info['city_result'].append(city_info)

    for province in json_data['more_city']:
        province_name = province['province']
        for city in province['city']:
            city_info = dict()
            city_info['category'] = province_name
            city_info['city_id'] = city['code']
            city_info['city_name'] = city['name']
            city_info['city_num'] = city['num']
            info['city_result'].append(city_info)
    return info


def write_cleaned_info_to_csv(info, path='data/baidumap_results/'):
    save_filename = path + info['keyword'] + '_' + datetime.datetime.now().strftime('%Y%m%d') + '.csv'
    if len(info['city_result']) == 0:
        print('No results found in: ', info['keyword'])
        return

    with open(save_filename, 'w+', encoding='gbk', newline='') as f:
        f.write('category,city_id,city_name,poi_num\n')
        for city in info['city_result']:
            line = city['category'] + ',' + str(city['city_id']) + ',' + \
                   city['city_name'] + ',' + str(city['city_num']) + '\n'
            f.write(line)
    print('Successfully write results to: ', save_filename)
    return
