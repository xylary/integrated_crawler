#!/usr/bin/python
# -*- coding: utf-8 -*-

from pipelines.pipeline_dianping import *

# search_keyword_in_dianping('肯德基', start_city_id=105)
# clean_data()


city_list = get_city_list(province='北京')
for city_info in city_list:
    get_all_records(city_info, channel=10, group=116)