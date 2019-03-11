from pipelines.pipeline_lianjia import *
from utils.db_oper import *


url_ershoufang = 'https://sh.lianjia.com/ershoufang/107100991859.html'
url_chengjiao = 'https://sh.lianjia.com/chengjiao/107000513345.html'
url_city_xiaoqu = 'https://sh.lianjia.com/xiaoqu/'
url_subdistrict = 'http://hz.lianjia.com/xiaoqu/hubin1/'


def update_xiaoqu_num_in_subdistrics(db_con):
    df = pd.read_sql('select city_abbr from city_map', con=cnx)
    cities = df['city_abbr'].tolist()

    for city in cities:
        if city not in ['aq', 'bj', 'sh', 'hz', 'sz', 'wh']:
            try:
                get_subdistrict_list_in_city(city)
            except Exception as e:
                print(e)


db_path = 'data/lianjia_data.db'
cnx = sqlite3.connect(db_path)


# get_city_list()
# get_xiaoqu_info_in_subdistict(url_subdistrict)
# get_xiaoqu_chengjiao_info(xiaoqu_id='5011000014141', city_abbr='sh')
# get_xiaoqu_ershoufang_info(xiaoqu_id='5011000014141', city_abbr='sh')
# get_xiaoqu_detailed_info(xiaoqu_id='57+999999011000014141', city_abbr='sh')