from utils.pipeline import *

url = 'https://sh.lianjia.com/zufang/c5011000016470/'
h = request_lianjia_url(url, lib='bs4')

print(get_total_pages(h, 'zufang'))
