#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.pipeline_dianping import *
import pandas as pd
import math


keyword = '麦嘉基'

bdmap_result_csvfile = 'data/baidumap_results/{}_20190220.csv'.format(keyword)

df_nierson = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')

city_id_list = sorted(list(df_nierson.meituan_city_id))

start_city_id = 1

start_crawler(keyword, city_id_list, start_city_id)
