import os
import time, datetime
import requests, re
from lxml import html
import lxml.cssselect as cssselect
import logging
import js2py, execjs


logging.basicConfig(filename='logs/utils_pipeline_jiameng.log', level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")


def request_jiameng_url(url, method='GET', max_retries=5, retries_interval=2, need_cookie=False):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    counter = 0
    while True:
        response = requests.request(method, url=url, headers=headers)
        if response.status_code == 200:
            print(str(response.status_code) + ': ' + url)
            break
        else:
            print('Status Code = ', response.status_code)
            print('Retrying to fetch transactions...')
            counter += 1
            if counter > max_retries:
                exit('Retries over {} times, program exit.'.format(str(max_retries)))
                time.sleep(retries_interval)

    h = html.fromstring(response.content)
    return h


def get_info_from_li(li_elem):
    info = dict()
    try:
        info['brand_name'] = clean(li_elem.cssselect('div.col.col-2 > div.clearfix > a')[0].text)
        info['food_category'] = clean(li_elem.cssselect('div.col.col-2 > div:nth-child(2)')[0].text_content())
        info['total_stores'] = clean(li_elem.cssselect('div.col.col-2 > div:nth-child(3)')[0].text_content())
        info['attendance_fee'] = clean(li_elem.cssselect('div.col.col-3 > dl:nth-child(1) > dd > span')[0].text)

        company_name = li_elem.cssselect('div.col.col-4 > div.m-company > a')[0].text
        if company_name is None:
            info['corp_name'] = 'N/A'
        else:
            info['corp_name'] = clean(company_name)
        info['corp_address'] = clean(li_elem.cssselect('div.col.col-4 > div.m-company > div.m-com-zone > span')[0].text)
        info['corp_type'] = clean(li_elem.cssselect('div.col.col-4 > div.m-company > div.showInfo > dl > dd')[0].text)
        info['corp_capital'] = clean(li_elem.cssselect('div.col.col-4 > div.m-company > div.showInfo > dl > dd')[1].text)
        info['corp_reg_date'] = clean(li_elem.cssselect('div.col.col-4 > div.m-company > div.showInfo > dl > dd')[2].text)
        info['corp_location'] = clean(li_elem.cssselect('div.col.col-4 > div.m-company > div.showInfo > dl > dd')[3].text)
    except Exception as e:
        logging.warning(e)
    return info


def get_info_on_page(html):
    info_list = []
    lis = html.find_class('items items_V clearfix')
    for li in lis:
        info_list.append(get_info_from_li(li))
    return info_list


def clean(s):
    to_be_cleaned_substrings = ['\n', '\r', '\t', '经营产品：', '门店数量：', '家']
    for substring in to_be_cleaned_substrings:
        s = s.replace(substring, '')
    s = s.replace('\xa0', ' ')
    return s


def get_info(base_url='http://so.jiameng.com/hubei_xican/p{}/htm?sort=1', max_page=84):
    list = []
    for i in range(1, max_page + 1):
        h = request_jiameng_url(url=base_url.format(str(i)))
        page_info = get_info_on_page(h)
        list += page_info
    return list



