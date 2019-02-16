from utils.pipeline_dianping import *
import pandas as pd


#get_city_id('dianping_city_list.csv')


keywords = '第1佳大鸡排'
start_city_id = 236

df3 = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
city_id_list = sorted(list(df3.meituan_city_id))
for city_id in city_id_list:
    if city_id >= start_city_id:
        total_number_in_city = search_restaurant_in_city(keywords, city_id)
        print(str(city_id) + ': ' + str(total_number_in_city))
        time.sleep(2.0)
