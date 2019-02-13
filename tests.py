from utils.pipeline import *

xiaoqu_url = 'https://sh.lianjia.com/xiaoqu/5011000016470/'
h = request_lianjia_url(xiaoqu_url, lib='bs4')

print(h.prettify())
