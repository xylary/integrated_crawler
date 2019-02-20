#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.selenium_webdriver import *


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



