# -*- coding: utf-8 -*-

import os, re
import time, datetime
import re
from utils.general_request import *
import logging


logging.basicConfig(filename='logs/utils_pipeline_lianjia.log', level=logging.DEBUG,
					format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL = 3
TIME_INTERVAL_SEARCH_SUBSTRICT = 1.0


def get_city_list():
	url_city = 'https://www.lianjia.com/city/'
	h = request_url_without_proxy(url_city)
	provinces = h.find_all('div', class_='city_province')
	with open('data/lianjia/lianjia_cities.csv', 'w+', encoding='gbk', newline='') as f:
		f.write('province,city,city_abbr,city_url\n')
		for province in provinces:
			province_name = province.find('div', class_='city_list_tit c_b').text
			links = province.find('ul').find_all('a')
			for link in links:
				city_name = link.text
				city_url = link.attrs['href']
				city_abbr = city_url.split('//')[-1].split('.')[0]
				line = province_name + ',' + city_name + ',' + city_abbr + ',' + city_url + '\n'
				f.write(line)
	print('Finished update LianJia cities.')


def get_total_pages(h, page_type):
	if page_type == 'zufang':
		class_name, attrib_name, sub_attrib_name = 'content__pg', 'data-totalpage', None
	else:
		class_name, attrib_name, sub_attrib_name = 'page-box house-lst-page-box', 'page-data', 'totalPage'

	if sub_attrib_name is None:
		c = h.find('div', class_=class_name)
		total_pages = int(c.attrs[attrib_name])
	else:
		c = h.find('div', class_=class_name)
		total_pages = eval(c.attrs[attrib_name])[sub_attrib_name]
	return total_pages


def get_list_contents(bs4_h, record_type):
	if record_type == 'ershoufang':
		records = bs4_h.find('li', class_="clear LOGCLICKDATA")
	elif record_type == 'chengjiao':
		records = bs4_h.find('ul', class_="listContent").find_all('li')
	return records


def get_record_links(city='sh', record_type='ershoufang', min_pages=1, max_pages=100):
	record_links = []
	base_url = "http://{}.lianjia.com/{}/".format(city, record_type)
	for i in range(min_pages, min(max_pages, 100) + 1):
		if i == 1:
			url = base_url
		else:
			url = base_url + 'pg' + str(i) + '/'
		h = request_url_without_proxy(url=url)
		records = get_list_contents(h)
		print('Transactions on the page = ', len(records))
		for record in records:
			link = record.cssselect('a')[0].attrib['href']
			print(link)
			record_links.append(link)
		time.sleep(1.0)
		if i % 5 == 0:
			print('{} / 100 pages has been fetched'.format(str(i)))
	return record_links


def get_ershoufang_house_info(ershoufang_house_url):
	info = dict()
	try:
		h = request_url_without_proxy(ershoufang_house_url)

		# Get property
		title_div = h.find('div', class_='title')
		info['title_1'] = title_div.find('h1').text
		info['title_2'] = title_div.find('div', class_='sub').attrs['title']
		info['region'] = h.find('div', class_='fl l-txt').text

		# Get attributes
		main_div = h.find('div', class_='houseInfo')
		info['structure'] = main_div.find_all('div', class_='mainInfo')[0].text
		info['facing'] = main_div.find_all('div', class_='mainInfo')[1].text
		info['area'] = main_div.find_all('div', class_='mainInfo')[2].text
		info['floor'] = main_div.find_all('div', class_='subInfo')[0].text
		info['furbishing'] = main_div.find_all('div', class_='subInfo')[1].text
		info['age'] = main_div.find_all('div', class_='subInfo')[2].text
		info['estate_name'] = h.find('div', class_='communityName').find_all('a')[0].text
		info['estate_uri'] = h.find('div', class_='communityName').find_all('a')[0].attrs['href']

		# Get pricing
		price_div = h.find('div', class_='price')
		info['total_price'] = price_div.find('span', class_='total').text
		info['unit_price'] = price_div.find('span', class_='unitPriceValue').text

		# Get Basic Info
		info['intro_contents'] = h.find('div', class_='base').text
		info['trxn_contents'] = h.find('div', class_='transaction').text

		# Get Layout Link & favour count
		info['favCount'] = int(h.find('span', {'id': 'favCount'}).text)
		info['layout_url'] = h.find('div', class_='imgdiv').attrs['data-img']

	except Exception as e:
		msg = 'Exception found when crawling page: ' + ershoufang_house_url + ' , \n'
		msg += str(e)
		print(msg)
		logging.error(msg)
	return info


def get_chengjiao_house_info(chengjiao_house_url):
	info = dict()
	try:
		h = request_url_without_proxy(chengjiao_house_url)

		# Get title
		info['status'] = 'sold'
		title_div = h.find('div', class_='wrapper')
		info['title'] = title_div.text
		info['transaction_date'] = title_div.find('span').text
		info['region'] = h.find('div', class_='deal-bread').text.replace('成交价格', '').replace('>', ' > ')

		# Get pricing
		main_div = h.find('div', class_='info fr')
		info['deal_price'] = float(main_div.find('span', class_='dealTotalPrice').find('i').text)
		info['unit_price'] = float(main_div.find('div', class_='price').find('b').text)

		# Get attributes
		spans = main_div.find('div', class_='msg').find_all('span')
		for span in spans:
			full_text = span.text
			value = span.find('label').text
			key = full_text.replace(value, '')
			info[key] = float(value)

		# Get Basic Info
		info['intro_contents'] = h.find('div', class_='base').text
		info['trxn_contents'] = h.find('div', class_='transaction').text

		# Get Layout Link
		small_pic_lis = h.find('div', class_='thumbnail').find('ul').find_all('li')
		for li in small_pic_lis:
			if li.attrs['data-desc'] == '户型图':
				img_url = li.attrs['data-src']
				splits = img_url.split('.')
				info['layout_base_url'] = '.'.join(splits[:-2])

	except Exception as e:
		msg = 'Exception found when crawling page: ' + chengjiao_house_url + ' , \n'
		msg += str(e)
		print(msg)
		logging.error(msg)
	return info


def get_house_info(house_url):
	if house_url.split('/')[-2] == 'ershoufang':
		info = get_ershoufang_house_info(house_url)
	elif house_url.split('/')[-2] == 'chengjiao':
		info = get_chengjiao_house_info(house_url)
	else:
		info = dict()
	return info


def get_xiaoqu_list(city='sh'):
	review_date = datetime.datetime.now().strftime('%Y%m%d')
	save_filename = 'data/lianjia/subdistrict_details_{}_{}.csv'.format(city, review_date)
	headline = 'city,district_name,subdistrict_name,subdistrict_xiaoqu_num,subdistrict_url\n'
	with open(save_filename, 'w+', encoding='gbk', newline='') as f:
		f.write(headline)

	base_url = "http://{}.lianjia.com".format(city)
	url = base_url + '/xiaoqu/'
	h1 = request_url_without_proxy(url=url)
	districts = h1.find('div', {'data-role': 'ershoufang'}).find_all('div')[0].find_all('a')

	for district in districts:
		district_name = district.text
		href_tag = district.attrs['href']
		h2 = request_url_without_proxy(base_url + href_tag)
		try:
			subdistricts = h2.find('div', {'data-role': 'ershoufang'}).find_all('div')[1].find_all('a')
			with open(save_filename, 'a+', encoding='gbk', newline='') as f:
				for subdistrict in subdistricts:
					subdistrict_name = subdistrict.text
					subdistrict_url = base_url + subdistrict.attrs['href']
					h3 = request_url_without_proxy(subdistrict_url)
					subdistrict_xiaoqu_num = h3.find('h2', class_='total fl').find('span').text
					line_list = [city, district_name, subdistrict_name, subdistrict_xiaoqu_num, subdistrict_url]
					f.write(','.join(line_list) + '\n')
					time.sleep(TIME_INTERVAL_SEARCH_SUBSTRICT)
		except Exception as e:
			if isinstance(e, IndexError):
				subdistrict_name = 'None'
				subdistrict_xiaoqu_num = h2.find('h2', class_='total fl').find('span').text
				subdistrict_url = base_url + href_tag
				line_list = [city, district_name, subdistrict_name, subdistrict_xiaoqu_num, subdistrict_url]
				with open(save_filename, 'a+', encoding='gbk', newline='') as f:
					f.write(','.join(line_list) + '\n')
		time.sleep(TIME_INTERVAL_SEARCH_SUBSTRICT)
	print('Finished searching xiaoqu in city: ', city)


def get_xiaoqu_info_in_subdistict(subdistrict_url):
	info = dict()
	h = request_url_without_proxy(subdistrict_url)
	info['total_xiaoqu_number'] = int(h.find_class('total fl')[0].cssselect('span')[0].text)
	total_pages = eval(h.find_class('page-box house-lst-page-box')[0].attrib['page-data'])['totalPage']
	info['subdistrict_xiaoqu'] = dict()
	for i in range(1, total_pages + 1):
		if i == 1:
			url = subdistrict_url
		else:
			url = subdistrict_url + 'pg' + str(i) + '/'
		h = request_url_without_proxy(url=url)
		xiaoqu_list = h.find_class('listContent')
		if len(xiaoqu_list) == 0:
			print('Found blank page on url: ', url)

		xiaoqu_lis = h.find_class('listContent')[0].cssselect('li')
		for xiaoqu_li in xiaoqu_lis:
			d = dict()
			xiaoqu_id = xiaoqu_li.attrib['data-housecode']
			d['xiaoqu_name'] = xiaoqu_li.cssselect('div.info > div.title > a')[0].text
			d['sold_in_90d'] = int(xiaoqu_li.cssselect('div.info > div.houseInfo > a')[0].text.replace('90天成交', '')[:-1])
			d['cur_rental'] = int(xiaoqu_li.cssselect('div.info > div.houseInfo > a')[1].text.replace('套正在出租', ''))
			d['cur_selling'] = int(xiaoqu_li.cssselect('div.xiaoquListItemRight > div.xiaoquListItemSellCount > a > span')[0].text)
			avg_price = xiaoqu_li.cssselect('div.xiaoquListItemRight > div.xiaoquListItemPrice > div.totalPrice > span')[0].text
			if avg_price == '暂无':
				d['avg_price'] = -1.0
			else:
				d['avg_price'] = float(avg_price)
			year = xiaoqu_li.cssselect('div.info > div.positionInfo')[0].text_content().split('/\xa0')[-1].split('年')[0]
			if year == '未知':
				d['year'] = -1
			else:
				d['year'] = int(year)
			info['subdistrict_xiaoqu'][xiaoqu_id] = d
	return info


def get_xiaoqu_detailed_info(xiaoqu_url, need_cookie=False):
	info = dict()
	city_abbr = xiaoqu_url[xiaoqu_url.find('//') + 2 : xiaoqu_url.find('.')]
	xiaoqu_id = xiaoqu_url.split('/')[-2]
	h = request_url_without_proxy(xiaoqu_url, lib='bs4')
	try:
		info['id'] = xiaoqu_id
		info['name'] = h.find("h1", class_="detailTitle").text
		info['city'] = city_abbr
		info['address'] = h.find("div", class_="detailDesc").text
		info['followers'] = int(h.find('div', class_='detailFollowedNum').find('span').text)
		info['hierarchy'] = h.find('div', class_='l-txt').text.replace('\xa0', ' ')
		info['avg_unit_selling_price'] = float(h.find('span', class_='xiaoquUnitPrice').text)
		contents = h.find_all('span', class_='xiaoquInfoContent')
		year = contents[0].text.replace('年建成 ', '')
		if year == '未知':
			info['year'] = 9999
		else:
			info['year'] = int(year)
		info['structure_type'] = contents[1].text
		maintenance_fee = contents[2].text.replace('元/平米/月', '')
		try:
			info['maintenance_fee'] = float(maintenance_fee)
		except:
			info['maintenance_fee'] = -1.0
		info['property_management_corp'] = contents[3].text
		info['developer'] = contents[4].text
		total_buildings = contents[5].text.replace('栋', '')
		try:
			info['total_buildings'] = int(total_buildings)
		except:
			info['total_buildings'] = -1
		total_apartments = contents[6].text.replace('户', '')
		try:
			info['total_apartments'] = int(total_apartments)
		except:
			info['total_apartments'] = -1
		info['nearby_facilities'] = contents[7].text
	except Exception as e:
		msg = 'Exception encountered when getting info from: ' + xiaoqu_url + ' as: ' + str(e)
		logging.debug(msg)
		logging.debug(h.text_content())

	zufang_url = xiaoqu_url.replace('xiaoqu/', 'zufang/c')
	ershoufang_url = xiaoqu_url.replace('xiaoqu/', 'ershoufang/c')
	chengjiao_url = xiaoqu_url.replace('xiaoqu/', 'chengjiao/c')
	zf = request_url_without_proxy(zufang_url, lib='bs4')
	es = request_url_without_proxy(ershoufang_url, lib='bs4')
	cj = request_url_without_proxy(chengjiao_url, lib='bs4')
	return info


def get_xiaoqu_zufang_info(xiaoqu_id, city_abbr):
	zufang_info = []
	base_url = 'https://{}.lianjia.com/zufang/c{}/'.format(city_abbr, xiaoqu_id)
	h = request_url_without_proxy(url=base_url, lib='bs4')
	total_pages = get_total_pages(h, page_type='zufang')
	items = h.find_all('div', class_='content__list--item')
	for item in items:
		info = {}
		info['zufang_id'] = item.find('div', class_='content__list--item--main').find('a').attrs['href']
		info['zufang_title'] = item.find('div', class_='content__list--item--main').find('a').text.replace('\n', '').replace(' ', '')
		info['city'] = city_abbr
		details = item.find('p', class_='content__list--item--des').text.replace(' ', '').replace('\n', '').split('/')
		info['district'] = details[0].split('-')[0]
		info['subdistrict'] = details[0].split('-')[1]
		info['area_sqm'] = details[1].replace('㎡', '')
		info['facing'] = details[2]
		info['huxing'] = details[3]
		info['floor'] = details[4]
		info['post_days'] = item.find('p', class_='content__list--item--time oneline').text.replace('发布', '')
		info['rent_rmb_per_month'] = int(item.find('em').text)
		zufang_info.append(info)
	for page in range(2, total_pages + 1):
		url = base_url.replace('/c', '/pg{}c'.format(page))
		h = request_url_without_proxy(url=url, lib='bs4')
		items = h.find_all('div', class_='content__list--item')
		for item in items:
			info = {}
			info['zufang_id'] = item.find('div', class_='content__list--item--main').find('a').attrs['href']
			info['zufang_title'] = item.find('div', class_='content__list--item--main').find('a').text.replace('\n',
																											   '').replace(
				' ', '')
			info['city'] = city_abbr
			details = item.find('p', class_='content__list--item--des').text.replace(' ', '').replace('\n', '').split(
				'/')
			info['district'] = details[0].split('-')[0]
			info['subdistrict'] = details[0].split('-')[1]
			info['area_sqm'] = details[1].replace('㎡', '')
			info['facing'] = details[2]
			info['huxing'] = details[3]
			info['floor'] = details[4]
			info['post_days'] = item.find('p', class_='content__list--item--time oneline').text.replace('发布', '')
			info['rent_rmb_per_month'] = int(item.find('em').text)
			zufang_info.append(info)
	return zufang_info


def get_xiaoqu_ershoufang_info(xiaoqu_id, city_abbr):
	ershoufang_info = []
	base_url = 'https://{}.lianjia.com/ershoufang/c{}/'.format(city_abbr, xiaoqu_id)
	url = base_url
	h = request_url_without_proxy(url=url, lib='bs4')
	total_pages = get_total_pages(h, page_type='ershoufang')
	items = h.find_all('li', class_='clear LOGCLICKDATA')
	for item in items:
		info = {}
		info['ershoufang_id'] = item.find('div', class_='title').find('a').attrs['data-housecode']
		info['ershoufang_href'] = item.find('div', class_='title').find('a').attrs['href']
		info['ershoufang_title'] = item.find('div', class_='title').find('a').text
		info['xiaoqu_id'] = xiaoqu_id
		info['xiaoqu_name'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[0]
		info['city'] = city_abbr
		# info['district'] = ''
		# info['subdistrict'] = ''
		# House Properties
		info['area_sqm'] = float(item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[2].replace('平米', ''))
		info['facing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[3]
		info['huxing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[1]
		endpoint = item.find('div', class_='positionInfo').text.find(')') + 1
		info['floor'] = item.find('div', class_='positionInfo').text[:endpoint]
		info['year'] = item.find('div', class_='positionInfo').text[endpoint:].split('年')[0]
		info['furbishing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[4]
		info['elevator'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[5]
		# House Sales Info
		info['total_selling_price'] = int(item.find('div', class_='totalPrice').find('span').text)
		info['unit_selling_price'] = int(item.find('div', class_='unitPrice').attrs['data-price'])
		follow_info_texts = item.find('div', class_='followInfo').text.replace(' ', '').split('/')
		info['watchers'] = int(follow_info_texts[0].replace('人关注', ''))
		info['visits'] = int(follow_info_texts[1].replace('次带看', '').replace('共', ''))
		info['post_days'] = follow_info_texts[2].replace('发布', '')
		ershoufang_info.append(info)
	for page in range(2, total_pages + 1):
		time.sleep(1.0)
		url = base_url.replace('/c' + xiaoqu_id, ('/pg{}c' + xiaoqu_id).format(page))
		h = request_url_without_proxy(url=url, lib='bs4')
		items = h.find_all('li', class_='clear LOGCLICKDATA')
		for item in items:
			info = {}
			info['ershoufang_id'] = item.find('div', class_='title').find('a').attrs['data-housecode']
			info['ershoufang_href'] = item.find('div', class_='title').find('a').attrs['href']
			info['ershoufang_title'] = item.find('div', class_='title').find('a').text
			info['xiaoqu_id'] = xiaoqu_id
			info['xiaoqu_name'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[0]
			info['city'] = city_abbr
			# info['district'] = ''
			# info['subdistrict'] = ''
			# House Properties
			info['area_sqm'] = float(
				item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[2].replace('平米', ''))
			info['facing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[3]
			info['huxing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[1]
			endpoint = item.find('div', class_='positionInfo').text.find(')') + 1
			info['floor'] = item.find('div', class_='positionInfo').text[:endpoint]
			info['year'] = item.find('div', class_='positionInfo').text[endpoint:].split('年')[0]
			info['furbishing'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[4]
			info['elevator'] = item.find('div', class_='houseInfo').text.replace(' ', '').split('|')[5]
			# House Sales Info
			info['total_selling_price'] = int(item.find('div', class_='totalPrice').find('span').text)
			info['unit_selling_price'] = int(item.find('div', class_='unitPrice').attrs['data-price'])
			follow_info_texts = item.find('div', class_='followInfo').text.replace(' ', '').split('/')
			info['watchers'] = int(follow_info_texts[0].replace('人关注', ''))
			info['visits'] = int(follow_info_texts[1].replace('次带看', '').replace('共', ''))
			info['post_days'] = int(follow_info_texts[1].replace('发布', ''))
			ershoufang_info.append(info)
	return ershoufang_info


def get_xiaoqu_chengjiao_info(xiaoqu_id, city_abbr):
	chengjiao_info = []
	base_url = 'https://{}.lianjia.com/chengjiao/c{}/'.format(city_abbr, xiaoqu_id)
	url = base_url
	h = request_url_without_proxy(url=url, lib='bs4')
	total_pages = get_total_pages(h, page_type='chengjiao')
	items = h.find('ul', class_='listContent').find_all('li')
	for item in items:
		info = {}
		info['chengjiao_href'] = item.find('div', class_='title').find('a').attrs['href']
		info['chengjiao_title'] = item.find('div', class_='title').find('a').text
		info['city'] = city_abbr
		# info['district'] = ''
		# info['subdistrict'] = ''
		info['area_sqm'] = float(item.find('div', class_='title').find('a').text.split(' ')[-1].replace('平米', ''))
		spans = item.find('span', class_='dealCycleTxt').find_all('span')
		if len(spans) == 2:
			info['total_selling_price'] = int(spans[0].text.replace('挂牌', '').replace('万', ''))
			info['post_to_deal_days'] = int(spans[1].text.replace('成交周期', '').replace('天', ''))
		elif len(spans) == 1:
			if spans[0].text.find('挂牌') > -1:
				info['total_selling_price'] = int(spans[0].text.replace('挂牌', '').replace('万', ''))
				info['post_to_deal_days'] = None
			else:
				info['total_selling_price'] = None
				info['post_to_deal_days'] = int(spans[0].text.replace('成交周期', '').replace('天', ''))
		else:
			print('挂牌/成交周期 not correct in: ', url)
			info['total_selling_price'] = None
			info['post_to_deal_days'] = None
		info['total_deal_price'] = int(item.find_all('span', class_='number')[0].text)
		info['unit_deal_price'] = int(item.find_all('span', class_='number')[1].text)
		info['deal_date'] = item.find('div', class_='dealDate').text.replace('.', '-')

		info['facing'] = item.find('div', class_='houseInfo').text.replace('\xa0', '').replace(' ', '').split('|')[0]
		info['huxing'] = item.find('div', class_='title').find('a').text.split(' ')[1]
		info['floor'] = item.find('div', class_='positionInfo').text.split(' ')[0]
		info['furbishing'] = item.find('div', class_='houseInfo').text.replace('\xa0','').replace(' ', '').split('|')[1]
		info['elevator'] = item.find('div', class_='houseInfo').text.replace('\xa0','').replace(' ', '').split('|')[2]
		info['year'] = item.find('div', class_='positionInfo').text.split(' ')[1].split('年')[0]
		chengjiao_info.append(info)
	for page in range(2, total_pages + 1):
		time.sleep(1.0)
		url = base_url.replace('/c' + xiaoqu_id, ('/pg{}c' + xiaoqu_id).format(page))
		h = request_url_without_proxy(url=url, lib='bs4')
		items = h.find('ul', class_='listContent').find_all('li')
		for item in items:
			info = {}
			info['chengjiao_href'] = item.find('div', class_='title').find('a').attrs['href']
			info['chengjiao_title'] = item.find('div', class_='title').find('a').text
			info['city'] = city_abbr
			# info['district'] = ''
			# info['subdistrict'] = ''
			info['area_sqm'] = float(item.find('div', class_='title').find('a').text.split(' ')[-1].replace('平米', ''))
			spans = item.find('span', class_='dealCycleTxt').find_all('span')
			if len(spans) == 2:
				info['total_selling_price'] = int(spans[0].text.replace('挂牌', '').replace('万', ''))
				info['post_to_deal_days'] = int(spans[1].text.replace('成交周期', '').replace('天', ''))
			elif len(spans) == 1:
				if spans[0].text.find('挂牌') > -1:
					info['total_selling_price'] = int(spans[0].text.replace('挂牌', '').replace('万', ''))
					info['post_to_deal_days'] = None
				else:
					info['total_selling_price'] = None
					info['post_to_deal_days'] = int(spans[0].text.replace('成交周期', '').replace('天', ''))
			else:
				print('挂牌/成交周期 not correct in: ', url)
				info['total_selling_price'] = None
				info['post_to_deal_days'] = None
			info['total_deal_price'] = int(item.find_all('span', class_='number')[0].text)
			info['unit_deal_price'] = int(item.find_all('span', class_='number')[1].text)
			info['deal_date'] = item.find('div', class_='dealDate').text.replace('.', '-')

			info['facing'] = item.find('div', class_='houseInfo').text.replace('\xa0', '').replace(' ', '').split('|')[
				0]
			info['huxing'] = item.find('div', class_='title').find('a').text.split(' ')[1]
			info['floor'] = item.find('div', class_='positionInfo').text.split(' ')[0]
			info['furbishing'] = \
			item.find('div', class_='houseInfo').text.replace('\xa0', '').replace(' ', '').split('|')[1]
			info['elevator'] = \
			item.find('div', class_='houseInfo').text.replace('\xa0', '').replace(' ', '').split('|')[2]
			info['year'] = item.find('div', class_='positionInfo').text.split(' ')[1].split('年')[0]
			chengjiao_info.append(info)
	return chengjiao_info


