#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.pipeline_dianping import *
import pandas as pd


#get_city_id('dianping_city_list.csv')


df3 = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
city_id_list = sorted(list(df3.meituan_city_id))
keyword = '麦卡基'
start_city_id = 71


start_crawler(keyword, city_id_list, start_city_id)
