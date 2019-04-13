# -*- coding: utf-8 -*-

import os, re
import time, datetime
import csv
import sqlite3 as sql
import ssl
import json
import pandas as pd
from utils.general_request import *


logging.basicConfig(filename='logs/utils_pipeline_dianping.log', level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL_TO_NEXT_PAGE = 2.0
TIME_INTERVAL_TO_NEXT_CITY = 2.0


PROVINCE_ID = {
'北京': 1,
'天津': 2,
'河北': 3,
'山西': 4,
'内蒙古': 5,
'辽宁': 6,
'吉林': 7,
'黑龙江': 8,
'上海': 9,
'江苏': 10,
'浙江': 11,
'安徽': 12,
'福建': 13,
'江西': 14,
'山东': 15,
'河南': 16,
'湖北': 17,
'湖南': 18,
'广东': 19,
'广西': 20,
'海南': 21,
'重庆': 22,
'四川': 23,
'贵州': 24,
'云南': 25,
'西藏': 26,
'陕西': 27,
'甘肃': 28,
'青海': 29,
'宁夏': 30,
'新疆': 31,
'香港': 31,
'澳门': 33,
'台湾': 34
}


def get_city_id(csvfilename):
    city_ids = dict()
    url = 'http://www.dianping.com/citylist'
    h = request_url(url, 'GET')
    groups = h.find_all('li', class_='letter-item')
    with open(csvfilename, 'w+', encoding='UTF-8', newline='') as csvfile:
        csvfile.write('city_name,city_url,city_id\n')
        for group in groups:
            print('Now finding cities whose first-letter = ' + group.find('div', class_='oneletter').text)
            city_links = group.find_all('a')
            for city_link in city_links:
                city = city_link.text
                city_url = 'http:' + city_link.attrs['href'] + '/'
                h = request_url(city_url, 'GET')
                start_point = str(h).find("'cityId'")
                end_point = str(h).find(",  // 城市id")
                city_id = str(h)[start_point + 11:end_point - 1]
                csvfile.write(city + ',' + city_url + ',' + city_id + '\n')
                time.sleep(TIME_INTERVAL_TO_NEXT_CITY)
    return city_ids


def get_total_pages(h):
    if h.find('div', class_='page') is None:
        total_pages = 1
    else:
        total_pages = int(h.find('div', class_='page').find_all('a')[-2].attrs['data-ga-page'])
    return total_pages


def get_all_restaurants_in_results(url, to_csv, add_proxy=True):
    h = request_url(url, add_proxy=add_proxy)
    total_number = 0
    total_pages = get_total_pages(h)
    cur_page = 1
    while True:
        not_found_div = h.find('div', class_='not-found')
        if not_found_div is None:
            shoplist = h.find('div', {'id': 'shop-all-list'})
            if shoplist is not None:
                lis = shoplist.find_all('li')
                total_number += len(lis)
                with open(to_csv, 'a+', encoding='UTF-8', newline='') as f:
                    for li in lis:
                        store_title = li.find('div', class_='tit').find('a').attrs['title']
                        store_id = li.find('div', class_='tit').find('a').attrs['data-shopid']
                        store_score = li.find('div', class_='comment').find('span').attrs['title']
                        store_comment_url = li.find('div', class_='comment').find('a').attrs['href']
                        store_status = li.find('span', class_='istopTrade')
                        if store_status is None:
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',\n'
                        elif store_status.text != '歇业/关闭':
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',歇业/关闭\n'
                        else:
                            line = store_id + ',' + store_title + ',' + store_score + ',' + store_comment_url + ',' + store_status.text + '\n'
                        f.write(line)
        else:
            print('Found {} restaurant in url: {}.'.format(str(0), url))
            return total_number

        cur_page += 1
        if cur_page <= total_pages:
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + 'p' + str(cur_page)
            else:
                url = url.replace('p' + str(cur_page - 1), 'p' + str(cur_page))
            h = request_url(url, add_proxy=add_proxy)
        else:
            print('Found {} restaurant in url: {}.'.format(str(total_number), url))
            return total_number


def search_restaurant_in_city(keywords, city_id):
    url = 'https://www.dianping.com/search/keyword/{}/10_{}'.format(str(city_id), keywords)
    h = request_url(url)
    detail_csvfile = 'data/dianping/raw/' + 'restaurant_details_' + keywords + '.csv'
    total_number = 0
    total_pages = get_total_pages(h)
    cur_page = 1
    while True:
        not_found_div = h.find('div', class_='not-found')
        if not_found_div is None:
            shoplist = h.find('div', {'id': 'shop-all-list'})
            if shoplist is not None:
                lis = shoplist.find_all('li')
                total_number += len(lis)
                with open(detail_csvfile, 'a+', encoding='UTF-8', newline='') as f:
                    for li in lis:
                        store_title = li.find('div', class_='tit').find('a').attrs['title']
                        store_id = li.find('div', class_='tit').find('a').attrs['data-shopid']
                        store_score = li.find('div', class_='comment').find('span').attrs['title']
                        store_comment_url = li.find('div', class_='comment').find('a').attrs['href']
                        store_status = li.find('span', class_='istopTrade')
                        if store_status is None:
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',\n'
                        elif store_status.text != '歇业/关闭':
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',歇业/关闭\n'
                        else:
                            line = str(city_id) + ',' + keywords + ',' + store_id + ',' + store_title + \
                                   ',' + store_score + ',' + store_comment_url + ',' + store_status.text + '\n'
                        f.write(line)
        else:
            print('Found {} restaurant in city_id: {}.'.format(str(0), str(city_id)))
            return total_number

        cur_page += 1
        if cur_page <= total_pages:
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + '/p' + str(cur_page)
            else:
                url = url.replace('/p' + str(cur_page - 1), '/p' + str(cur_page))
            h = request_url(url)
        else:
            print('Found {} restaurant in city_id: {}.'.format(str(total_number), str(city_id)))
            return total_number


def start_crawler(keyword, city_id_list, start_city_id):
    for city_id in city_id_list:
        if city_id >= start_city_id:
            total_number_in_city = search_restaurant_in_city(keyword, city_id)
            print('Total results in city: {}  == {}.'.format(str(city_id), str(total_number_in_city)))
            time.sleep(2.0)
    print(requests.get(url_to_del_whitelist + PROXY.split(':')[0]).text)


def search_keyword_in_dianping(keyword, start_city_id=1):
    # If using baidu map source:
    # bdmap_result_csvfile = 'data/baidumap_results/{}_20190220.csv'.format(keyword)
    df_nierson = pd.read_csv('data/dianping/nierson_city_list.csv', encoding='gbk')
    city_id_list = sorted(list(df_nierson.meituan_city_id))
    start_crawler(keyword, city_id_list, start_city_id)
    print('Finished crawling info of: ', keyword)


def clean_csv_results(csvfilename):
    try:
        df = pd.read_csv(csvfilename,
                         names=['city_id', 'keyword', 'dianping_shop_id', 'shop_title', 'stars', 'shop_url', 'state'],
                         encoding='UTF-8')
    except UnicodeDecodeError as e1:
        df = pd.read_csv(csvfilename,
                         names=['city_id', 'keyword', 'dianping_shop_id', 'shop_title', 'stars', 'shop_url', 'state'],
                         encoding='gbk')
    except Exception as e2:
        print('Exception found when cleaning: ', csvfilename)
        print(e2)
        return
    finally:
        df = df.drop_duplicates(keep='first')
        new_name = csvfilename.replace('raw', 'cleaned')
        df.to_csv(new_name, encoding='utf-8')
        print('Finished cleaning file: ' + csvfilename)


def clean_data(path='data/dianping/raw/'):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if name not in ['dianping_city_list.csv', 'nierson_city_list.csv']:
                clean_csv_results(path + name)
    print('Finished cleaning data.')


def merge_cleaned_data(folder_path='dianping/cleaned/'):
    dfs = []
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            df = pd.read_csv(folder_path + name, encoding='gbk')
            dfs.append(df)
    df = pd.concat(dfs)
    df.to_csv('dianping_cleaned_in_one.csv', encoding='gbk')


def get_category_page_urls_in_city(city_url):
    hrefs = []
    h = request_url(city_url, add_proxy=False)
    try:
        lis = h.find_all('div', class_='content city-content')[0].find_all('li')
        for li in lis:
            href = li.find('a').attrs['href']
            hrefs.append(href)
    except IndexError:
        hrefs.append(city_url)
    return hrefs


def get_all_records(city_info, channel, group):
    city = city_info['cityEnName']
    url = 'http://www.dianping.com/{}/ch{}/g{}'.format(city, str(channel), str(group))
    csvfilename = city_info['cityName'] + '_ch' + str(channel) + '_g' + str(group) + '.csv'
    hrefs = get_category_page_urls_in_city(url)
    total_records = 0
    for href in hrefs:
        total_records += get_all_restaurants_in_results(href, csvfilename, add_proxy=True)
    print('Total records in {} channel {} group {} = {}'.format(city, str(channel), str(group), str(total_records)))
    return total_records


def get_city_list(province):
    province_id = PROVINCE_ID[province]
    r = requests.post('http://www.dianping.com/ajax/citylist/getDomesticCityByProvince',
                      json={'provinceId': province_id})
    city_list = json.loads(r.content)['cityList']
    return city_list


def update_css(bs4_elem, replace_needed=False):
    css_elems = bs4_elem.find('head').find_all('link', type='text/css')
    path = 'data/dianping/css/'
    global headers
    for css_elem in css_elems:
        if css_elem.attrs['href'].find('svg') != -1:
            css_url = 'http:' + css_elem.attrs['href']
            filename = css_url.split('/')[-1]
            if not os.path.exists(path + filename):
                print('Adding new css file: ' + filename)
                print('css file source: ' + css_url)
                r = requests.get(css_url, headers=headers)
                if r.status_code == 200:
                    with open(path + filename, 'w+', encoding='UTF-8', newline='') as f:
                        f.write(r.text)
            else:
                if replace_needed:
                    print('Updating css file: ' + filename)
                    print('css file source: ' + css_url)
                    r = requests.get(css_url, headers=headers)
                    if r.status_code == 200:
                        with open(path + filename, 'w+', encoding='UTF-8', newline='') as f:
                            f.write(r.text)
    return path + filename


def analyze_css(css_filename):
    with open(css_filename, 'r', encoding='UTF-8', newline='') as f:
        lines = f.readlines()
    cssfile = ''
    for line in lines:
        cssfile += line.replace('\n', '')
    items = cssfile.split('}')
    spans = []
    classes = []
    for item in items:
        try:
            if len(item) > 0:
                if item[:4] == 'span':
                    spans.append(item)
                elif item[0] == '.':
                    classes.append(item)
                else:
                    print(item)
        except Exception as e:
            print(e)
            print(item)

    codes = dict()
    for c in classes:
        key = c.split('{')[0][1:]
        x = float(c.split(':')[-1][:-1].replace('px', '').split(' ')[0])
        y = float(c.split(':')[-1][:-1].replace('px', '').split(' ')[1])
        codes[key] = (x, y)

    svg_hrefs = dict()
    for s in spans:
        key = re.search('class\^=".*"', s).group(0).split('"')[1]
        pairs = s.split('{')[-1].split(';')[:-1]
        d = {}
        for p in pairs:
            p = p.replace(': ', ':')
            k = p.split(':')[0]
            v = p.split(':')[1]
            if v.find('px') != -1:
                v = float(v.split('px')[0])
            if k == 'background-image':
                v = v[:-1].replace('url(', 'http:')
            d[k] = v
        svg_hrefs[key] = d

    return codes, svg_hrefs


def update_svg(svg_hrefs, replace_needed=False):
    path = 'data/dianping/svg/'
    global headers
    for value in svg_hrefs.values():
        bg_img_url = value['background-image']
        filename = bg_img_url.split('/')[-1]
        if not os.path.exists(path + filename):
            print('Adding new svg file: ' + filename)
            print('svg file source: ' + bg_img_url)
            r = requests.get(bg_img_url, headers=headers)
            if r.status_code == 200:
                with open(path + filename, 'w+', encoding='UTF-8', newline='') as f:
                    f.write(r.text)
        else:
            if replace_needed:
                print('Updating svg file: ' + filename)
                print('svg file source: ' + bg_img_url)
                r = requests.get(bg_img_url, headers=headers)
                if r.status_code == 200:
                    with open(path + filename, 'w+', encoding='UTF-8', newline='') as f:
                        f.write(r.text)
        time.sleep(0.5)
    print('Finished updating svg files.')


def decode_svg(svg_filename):
    with open(svg_filename, 'r', encoding='UTF-8', newline='') as f:
        lines = f.readlines()
    str = ''
    for line in lines:
        str += line
    s = bs4.BeautifulSoup(str, 'lxml')
    l = list()
    style_str = s.find('style').text
    result = re.search('font-size:\d*px', style_str).group(0)
    font_size=int(result[10:-2])
    height = float(s.find('svg').attrs['height'][:-2])
    width = float(s.find('svg').attrs['width'][:-2])
    l.append([0, width, height, font_size])
    if s.find('defs') is None:
        svg_type = 'text'
        texts = s.find_all('text')
        for i in range(len(texts)):
            row_id = i + 1
            row_x = float(texts[i].attrs['x'].split(' ')[0])
            row_y = float(texts[i].attrs['y'])
            row_text = texts[i].text
            l.append([row_id, row_x, row_y, row_text])
    else:
        svg_type = 'text_path'
        paths = s.find_all('path')
        text_paths = s.find_all('textpath')
        for i in range(len(paths)):
            row_y = float(paths[i].attrs['d'].split(' ')[1])
            row_width = float(text_paths[i].attrs['textlength'])
            row_text = text_paths[i].text
            row_id = int(text_paths[i].attrs['xlink:href'].replace('#', ''))
            l.append([row_id, row_width, row_y, row_text])
    decoded_svg = {
        'type': svg_type,
        'data': l
    }
    return decoded_svg


def get_letter_from_decoded_svg(decoded_svg, coordinates):
    letter = None
    svg_width = decoded_svg['data'][0][1]
    svg_height = decoded_svg['data'][0][2]
    svg_font_size = decoded_svg['data'][0][3]
    row_text = ''
    x, y = coordinates

    if x > svg_width or y > svg_height:
        print('The given coordinates is out of the svg.')
        letter = '[X]'

    elif decoded_svg['type'] == 'text_path':
        for i in range(1, len(decoded_svg['data'])):
            if decoded_svg['data'][i][2] <= y <= decoded_svg['data'][i][2] + svg_font_size:
                row_id = i
                row_text = decoded_svg['data'][i][3]
                break
        if row_text != '':
            letter_id = int(x // svg_font_size)
            letter = row_text[letter_id]
        else:
            print('Cannot locate the letter on the given coordinates.')
            letter = '[X]'

    elif decoded_svg['type'] == 'text':
        for i in range(1, len(decoded_svg['data'])):
            if decoded_svg['data'][i][2] <= y <= decoded_svg['data'][i][2] + svg_font_size:
                row_id = i
                row_text = decoded_svg['data'][i][3]
                break
        if row_text != '':
            letter_id = int((x - decoded_svg['data'][row_id][1]) // svg_font_size)
            letter = row_text[letter_id]
        else:
            print('Cannot locate the letter on the given coordinates.')
            letter = '[X]'

    else:
        print('The type of the decoded_svg is unknown, please check.')
        letter = '[X]'
    return letter


def class_to_letter(letter_class, codes, svg_hrefs):

    for key in svg_hrefs.keys():
        if key == letter_class[:len(key)]:
            svg_href = svg_hrefs[key]
            break

    code = codes[letter_class]
    svg_path = 'data/dianping/svg/'
    svg_filename = svg_href['background-image'].split('/')[-1]
    decoded_svg = decode_svg(svg_path + svg_filename)

    if 'margin-left' in svg_href.keys():
        svg_x =  - svg_href['margin-left'] - code[0]
    else:
        svg_x = - code[0]

    svg_y = - svg_href['margin-top'] - code[1] + svg_href['height'] / 2.0
    coordinates = (svg_x, svg_y)
    letter = get_letter_from_decoded_svg(decoded_svg, coordinates)

    return letter


def get_info_of_li(li_elem, codes, svg_hrefs):

    pic = li_elem.find('div', class_='pic')
    txt = li_elem.find('div', class_='txt')
    opr = li_elem.find('div', class_='operate')
    svr = li_elem.find('div', class_='svr-info')


    tit = txt.find('div', class_='tit')
    comment = txt.find('div', class_='comment')
    tag_addr = txt.find('div', class_='tag-addr')
    # recommend = txt.find('div', class_='recommend')
    # comment_list = txt.find('div', class_='comment-list')


    # .tit information
    shop_title = tit.find('a', {'data-click-name': 'shop_title_click'}).attrs['title']
    shop_id = tit.find('a', {'data-click-name': 'shop_title_click'}).attrs['data-shopid']
    shop_href = tit.find('a', {'data-click-name': 'shop_title_click'}).attrs['href']
    promo_icons = tit.find('div', class_='promo-icon').find_all('a')
    icons = []
    if len(promo_icons) > 0:
        for promo_icon in promo_icons:
            icons.append(promo_icon.attrs['data-click-name'])

    if tit.find('a', {'data-click-name': 'shop_icon_ad_click'}) is not None:
        is_advertising = 1
    else:
        is_advertising = 0


    # .comment information
    stars = comment.find('span', class_='sml-rank-stars').attrs['title']
    review_num = convert_contents(comment.find('a', class_='review-num').find('b').contents,
                                  codes, svg_hrefs)
    mean_price = convert_contents(comment.find('a', class_='mean-price').find('b').contents,
                                  codes, svg_hrefs)


    # .tag-addr information
    category = convert_contents(
                tag_addr.find('a', {'data-click-name': 'shop_tag_cate_click'}).find('span', class_='tag').contents,
                codes, svg_hrefs)
    region = convert_contents(
                tag_addr.find('a', {'data-click-name': 'shop_tag_region_click'}).find('span', class_='tag').contents,
                codes, svg_hrefs)
    address = convert_contents(tag_addr.find('span', class_='addr').contents, codes, svg_hrefs)

    info = {
        'shop_id': shop_id,
        'shop_title': shop_title,
        'shop_href': shop_href,
        'icons': icons,
        'is_advertising': is_advertising,
        'stars': stars,
        'review_num': review_num,
        'mean_price': mean_price,
        'category': category,
        'region': region,
        'address': address
    }

    return info


def convert_contents(contents, codes, svg_hrefs):
    line = ''
    for content in contents:
        if isinstance(content, bs4.element.Tag):
            code = content.attrs['class'][0]
            letter = class_to_letter(code, codes, svg_hrefs)
            line += letter
        elif isinstance(content, bs4.element.NavigableString):
            line += str(content)
    return line


def get_all_restaurants_info(url, to_csv, add_proxy=True):
    h = request_url(url, add_proxy=add_proxy)
    css_filename = update_css(h, replace_needed=True)
    codes, svg_hrefs = analyze_css(css_filename)
    update_svg(svg_hrefs, replace_needed=True)
    total_number = 0
    total_pages = get_total_pages(h)
    cur_page = 1
    while True:
        not_found_div = h.find('div', class_='not-found')
        if not_found_div is None:
            shoplist = h.find('div', {'id': 'shop-all-list'})
            if shoplist is not None:
                lis = shoplist.find_all('li')
                total_number += len(lis)
                for li in lis:
                    li_info = get_info_of_li(li, codes, svg_hrefs)
                    for k, v in li_info.items():
                        print(k, v)
        else:
            print('Found {} restaurant in url: {}.'.format(str(0), url))
            return total_number

        cur_page += 1
        if cur_page <= total_pages:
            time.sleep(TIME_INTERVAL_TO_NEXT_PAGE)
            if cur_page == 2:
                url = url + 'p' + str(cur_page)
            else:
                url = url.replace('p' + str(cur_page - 1), 'p' + str(cur_page))
            h = request_url(url, add_proxy=add_proxy)
        else:
            print('Found {} restaurant in url: {}.'.format(str(total_number), url))
            return total_number