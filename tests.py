from utils.pipeline import *

# url = 'https://sh.lianjia.com/zufang/c5011000016470/'
# h = request_lianjia_url(url, lib='bs4')
info = get_xiaoqu_zufang_info('5011000016470', 'sh')
print(info)
