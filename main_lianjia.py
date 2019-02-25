from pipelines.pipeline_lianjia import *


url_ershoufang = 'https://sh.lianjia.com/ershoufang/107100991859.html'
url_chengjiao = 'https://sh.lianjia.com/chengjiao/107000513345.html'
url_city_xiaoqu = 'https://sh.lianjia.com/xiaoqu/'
url_subdistrict = 'http://sh.lianjia.com/xiaoqu/changshoulu/'

# get_xiaoqu_list('hz')
# get_city_list()
# get_xiaoqu_info_in_subdistict(url_subdistrict)
get_xiaoqu_chengjiao_info(xiaoqu_id='5011000014141', city_abbr='sh')
get_xiaoqu_ershoufang_info(xiaoqu_id='5011000014141', city_abbr='sh')
get_xiaoqu_detailed_info(xiaoqu_id='5011000014141', city_abbr='sh')