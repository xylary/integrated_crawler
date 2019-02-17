#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.pipeline_dianping import *
import pandas as pd


#get_city_id('dianping_city_list.csv')


df3 = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
city_id_list = sorted(list(df3.meituan_city_id))
keyword = '多伦多海鲜自助'
start_city_id = 290


for city_id in city_id_list:
    if city_id >= start_city_id:
        total_number_in_city = search_restaurant_in_city(keyword, city_id)
        print('Total results in city: {}  == {}.'.format(str(city_id), str(total_number_in_city)))
        time.sleep(2.0)
