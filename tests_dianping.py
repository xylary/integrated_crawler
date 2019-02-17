from utils.pipeline_dianping import *
import pandas as pd


#get_city_id('dianping_city_list.csv')


keywords = ['萨贝尔', '佳客来牛排', '百特喜']
start_city_id = 120


proxy_pool = ['58.218.198.182:18787', '58.218.198.190:4188', '58.218.198.145:17362', '58.218.92.128:13537', '58.218.198.190:4578']

df3 = pd.read_csv('dianping_results/nierson_city_list.csv', encoding='gbk')
city_id_list = sorted(list(df3.meituan_city_id))
for keyword in keywords:
    for city_id in city_id_list:
        if city_id >= start_city_id:
            total_number_in_city = search_restaurant_in_city(keyword, city_id)
            print(str(city_id) + ': ' + str(total_number_in_city))
            time.sleep(2.0)
    start_city_id = 1