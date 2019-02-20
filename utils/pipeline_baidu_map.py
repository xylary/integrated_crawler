#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.selenium_webdriver import *


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
