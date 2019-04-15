from pipelines.pipeline_baidu_map import *
import json


keywords = [
    '麦乐基', '功夫鸡排', '蓝蛙', '享哆味', '第1佳大鸡排',
    '麦肯基', '加州汉堡', '麦加美汉堡', '曼可基', '巴比汉堡'
]


# searching_keywords_on_baidumap(keywords)


with open('data/baidu_map_result.txt', 'r+', encoding='UTF-8', newline='') as f:
    lines = f.readlines()


for line in lines:
    r = json.loads(line)
    info = read_country_result(r)
    write_cleaned_info_to_csv(info)
