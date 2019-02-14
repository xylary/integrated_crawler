import os
import time, datetime
import requests, re
from lxml import html
import lxml.cssselect as cssselect
import logging
import js2py, execjs
import bs4


logging.basicConfig(filename='logs/utils_pipeline.log', level=logging.DEBUG,
					format="%(asctime)s - %(levelname)s - %(message)s",
					datefmt="%m/%d/%Y %H:%M:%S %p")

TIME_INTERVAL = 3


def request_lianjia_url(url, method='GET', max_retries=5, **kwargs):
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
	}
	if 'cookie' in kwargs.keys():
		headers['cookie'] = kwargs['cookie']
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
			time.sleep(TIME_INTERVAL * 1.5)

	if 'lib' in kwargs.keys() and kwargs['lib'] == 'bs4':
		h = bs4.BeautifulSoup(response.content, 'lxml')
	else:
		h = html.fromstring(response.content)
	return h


def get_total_pages(h, page_type):
	if page_type == 'zufang':
		class_name, attrib_name, sub_attrib_name = 'content__pg', 'data-totalpage', None
	else:
		class_name, attrib_name, sub_attrib_name = 'page-box house-lst-page-box', 'page-data', 'totalPage'

	if type(h) is html.HtmlElement:
		total_pages = eval(h.find_class(class_name)[0].attrib[attrib_name])[sub_attrib_name]
	elif type(h) is bs4.BeautifulSoup:
		if sub_attrib_name is None:
			c = h.find('div', class_=class_name)
			total_pages = int(c.attrs[attrib_name])
		else:
			c = h.find('div', class_=class_name)
			total_pages = eval(c.attrs[attrib_name])[sub_attrib_name]
	else:
		raise AssertionError("Type of the input is not 'bs4.Beautiful' or 'lxml.html.HtmlElement'.")
	return total_pages


def get_record_links(city='sh', record_type='ershoufang', min_pages=1, max_pages=100):
	record_links = []
	base_url = "http://{}.lianjia.com/{}/".format(city, record_type)
	for i in range(min_pages, min(max_pages, 100) + 1):
		if i == 1:
			url = base_url
		else:
			url = base_url + 'pg' + str(i) + '/'

		h = request_lianjia_url(url=url)

		if record_type == 'ershoufang':
			records = h.find_class("clear LOGCLICKDATA")
		elif record_type == 'chengjiao':
			records = h.find_class("listContent")[0].cssselect('li')

		print('Transactions on the page = ', len(records))

		for record in records:
			link = record.cssselect('a')[0].attrib['href']
			print(link)
			record_links.append(link)

		time.sleep(1.0)
		if i % 5 == 0:
			print('{} / 100 pages has been fetched'.format(str(i)))

	return record_links


def get_house_info(house_url):
	info = dict()
	h = request_lianjia_url(house_url)
	try:
		if house_url.split('/')[-2] == 'ershoufang':
			info['status'] = 'selling'

			# Get title
			title_div = h.cssselect('body > div.sellDetailHeader > div > div > div.title')[0]
			info['title_1'] = title_div.cssselect('h1')[0].text
			info['title_2'] = title_div.cssselect('div.sub')[0].attrib['title']

			# Get region
			region_div = h.find_class('fl l-txt')[0]
			region = ''
			for child in region_div.getchildren():
				region += child.text
			info['region'] = region.replace('\xa0', ' ')

			main_div = h.cssselect('body > div.overview > div.content')[0]
			# Get pricing
			info['total_price'] = float(main_div.find_class('total')[0].text)
			info['unit_price'] = float(main_div.find_class('unitPriceValue')[0].text)
			# Get attributes
			info['structure'] = main_div.cssselect('div.houseInfo > div.room > div.mainInfo')[0].text
			info['floor'] = main_div.cssselect('div.houseInfo > div.room > div.subInfo')[0].text
			info['facing'] = main_div.cssselect('div.houseInfo > div.type > div.mainInfo')[0].text
			info['furbishing'] = main_div.cssselect('div.houseInfo > div.type > div.subInfo')[0].text
			info['area'] = main_div.cssselect('div.houseInfo > div.area > div.mainInfo')[0].text
			info['age'] = main_div.cssselect('div.houseInfo > div.area > div.subInfo')[0].text
			info['estate_name'] = main_div.cssselect('div.aroundInfo > div.communityName > a.info ')[0].text
			info['estate_uri'] = main_div.cssselect('div.aroundInfo > div.communityName > a.info ')[0].attrib['href']

			# Get Basic Info
			d = dict()
			contents = h.get_element_by_id('introduction').find_class('content')
			for content in contents:
				for row in content.cssselect('ul > li'):
					key = row.cssselect('span')[0].text
					value = row.text_content().replace(' ', '').replace('\n', '')
					d[key] = value.replace(key, '')
			info['basics'] = d

			# Get Layout Link & favour count
			info['favCount'] = int(h.get_element_by_id('favCount').text)
			img_div = h.get_element_by_id('layout').cssselect('div.layout > div.content > div.imgdiv')[0]
			info['layout_base_url'] = img_div.attrib['data-img']

		elif house_url.split('/')[-2] == 'chengjiao':
			info['status'] = 'sold'

			# Get title
			title_div = h.find_class('house-title')[0].cssselect('div.wrapper')[0]
			info['title'] = title_div.text
			info['transaction_date'] = title_div.cssselect('span')[0].text

			# Get region
			region_div = h.find_class('deal-bread')[0]
			region = ''
			for child in region_div.getchildren():
				region += child.text.replace('成交价格', ' ')
			info['region'] = region.replace('\xa0', ' ') + ' 当前房源'

			main_div = h.find_class('info fr')[0]
			# Get pricing
			info['deal_price'] = float(main_div.cssselect('div.price > span.dealTotalPrice > i')[0].text)
			info['unit_price'] = float(main_div.cssselect('div.price > b')[0].text)
			# Get attributes
			spans = main_div.cssselect('div.msg > span')
			for span in spans:
				full_text = span.text_content()
				value = span.cssselect('label')[0].text
				key = full_text.replace(value, '')
				info[key] = float(value)

			# Get Basic Info
			d = dict()
			contents = h.get_element_by_id('introduction').find_class('content')
			for content in contents:
				for row in content.cssselect('ul > li'):
					key = row.cssselect('span')[0].text
					value = row.text_content().replace(' ', '').replace('\n', '')
					d[key] = value.replace(key, '')
			info['basics'] = d

			# Get Layout Link
			small_pic_lis = h.get_element_by_id('thumbnail2').cssselect('ul > li')
			for li in small_pic_lis:
				if li.attrib['data-desc'] == '户型图':
					img_url = li.attrib['data-src']
					end_point = img_url.find('.png') + 4
					info['layout_base_url'] = img_url[:end_point]

	except Exception as e:
		print('While processing url "', house_url, '", exception occurred as: ')
		print(e)

	return info


def get_xiaoqu_list(city='sh', time_interval=1.0):
	xiaoqu = dict()
	base_url = "http://{}.lianjia.com".format(city)

	url = base_url + '/xiaoqu/'
	h1 = request_lianjia_url(url=url)
	districts = h1.cssselect('body > div.m-filter > div.position > dl:nth-child(2) > dd > div > div > a')

	for district in districts:
		xiaoqu[district.text] = dict()
		href_tag = district.attrib['href']
		h2 = request_lianjia_url(base_url + href_tag)
		subdistricts = h2.cssselect('body > div.m-filter > div.position > dl:nth-child(2) > dd > div > div:nth-child(2) > a')
		for subdistrict in subdistricts:
			xiaoqu[district.text][subdistrict.text] = dict()
			url = base_url + subdistrict.attrib['href']
			xiaoqu[district.text][subdistrict.text]['subdistrict_url'] = url
			d = get_xiaoqu_info_in_subdistict(url)
			xiaoqu[district.text][subdistrict.text]['subdistrict_xiaoqu_number'] = d['total_xiaoqu_number']
			xiaoqu[district.text][subdistrict.text]['subdistrict_xiaoqu_number'] = d['subdistrict_xiaoqu']
			print(xiaoqu[district.text][subdistrict.text])

		time.sleep(time_interval)

	return xiaoqu


def get_xiaoqu_info_in_subdistict(subdistrict_url):
	info = dict()
	h = request_lianjia_url(subdistrict_url)
	info['total_xiaoqu_number'] = int(h.find_class('total fl')[0].cssselect('span')[0].text)
	total_pages = eval(h.find_class('page-box house-lst-page-box')[0].attrib['page-data'])['totalPage']
	info['subdistrict_xiaoqu'] = dict()
	for i in range(1, total_pages + 1):
		if i == 1:
			url = subdistrict_url
		else:
			url = subdistrict_url + 'pg' + str(i) + '/'
		h = request_lianjia_url(url=url)
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
	h = request_lianjia_url(xiaoqu_url, lib='bs4')
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
	zf = request_lianjia_url(zufang_url, lib='bs4')
	es = request_lianjia_url(ershoufang_url, lib='bs4')
	cj = request_lianjia_url(chengjiao_url, lib='bs4')
	return info


def get_xiaoqu_zufang_info(xiaoqu_id, city_abbr):
	zufang_info = []
	base_url = 'https://{}.lianjia.com/zufang/c{}/'.format(city_abbr, xiaoqu_id)
	h = request_lianjia_url(url=base_url, lib='bs4')
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
		h = request_lianjia_url(url=url, lib='bs4')
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
	h = request_lianjia_url(url=base_url, lib='bs4')
	total_pages = get_total_pages(h, page_type='ershoufang')
	items = h.find_all('div', class_='content__list--item')
	for item in items:
		info = {}
		info['zufang_id'] = ''
		info['zufang_title'] = ''
		info['city'] = city_abbr
		info['district'] = ''
		info['subdistrict'] = ''
		info['area_sqm'] = ''
		info['facing'] = ''
		info['huxing'] = ''
		info['brand'] = ''
		info['post_days'] = ''
		info['rent_rmb_per_month'] = ''
		ershoufang_info.append(info)
	for page in range(2, total_pages + 1):
		url = base_url.replace('/c', '/pg{}c'.format(page))
		h = request_lianjia_url(url=url, lib='bs4')
		items = h.find_all('div', class_='content__list--item')
		for item in items:
			info = {}
			info['zufang_id'] = ''
			info['zufang_title'] = ''
			info['city'] = city_abbr
			info['district'] = ''
			info['subdistrict'] = ''
			info['area_sqm'] = ''
			info['facing'] = ''
			info['huxing'] = ''
			info['brand'] = ''
			info['post_days'] = ''
			info['rent_rmb_per_month'] = ''
			ershoufang_info.append(info)
	return ershoufang_info


def get_xiaoqu_chengjiao_info(xiaoqu_id, city_abbr):
	chengjiao_info = []
	base_url = 'https://{}.lianjia.com/chengjiao/c{}/'.format(city_abbr, xiaoqu_id)
	h = request_lianjia_url(url=base_url, lib='bs4')
	total_pages = get_total_pages(h, page_type='chengjiao')
	items = h.find_all('div', class_='content__list--item')
	for item in items:
		info = {}
		info['zufang_id'] = ''
		info['zufang_title'] = ''
		info['city'] = city_abbr
		info['district'] = ''
		info['subdistrict'] = ''
		info['area_sqm'] = ''
		info['facing'] = ''
		info['huxing'] = ''
		info['brand'] = ''
		info['post_days'] = ''
		info['rent_rmb_per_month'] = ''
		chengjiao_info.append(info)
	for page in range(2, total_pages + 1):
		url = base_url.replace('/c', '/pg{}c'.format(page))
		h = request_lianjia_url(url=url, lib='bs4')
		items = h.find_all('div', class_='content__list--item')
		for item in items:
			info = {}
			info['zufang_id'] = ''
			info['zufang_title'] = ''
			info['city'] = city_abbr
			info['district'] = ''
			info['subdistrict'] = ''
			info['area_sqm'] = ''
			info['facing'] = ''
			info['huxing'] = ''
			info['brand'] = ''
			info['post_days'] = ''
			info['rent_rmb_per_month'] = ''
			chengjiao_info.append(info)
	return chengjiao_info


