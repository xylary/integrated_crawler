#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.pipeline_dianping import *
import pandas as pd
import math



keyword = '麦卡基'


bdmap_result_csvfile = 'data/baidumap_results/{}_20190220.csv'.format(keyword)
df_bd = pd.read_csv(bdmap_result_csvfile, encoding='gbk')
df_bd.index = df_bd.city_name
df_nierson = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
df_nierson.index = df_nierson.city

df = pd.concat([df_bd, df_nierson], axis=1, join_axes=[df_bd.index])
city_id_list = sorted(list(df.meituan_city_id))
city_id_list_cleaned = []
for city_id in city_id_list:
    if not math.isnan(city_id):
        city_id_list_cleaned.append(int(city_id))

print(city_id_list_cleaned)

start_city_id = 1
start_crawler(keyword, city_id_list_cleaned, start_city_id)
