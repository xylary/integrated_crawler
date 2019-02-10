import os
import time, datetime
import requests, re
from lxml import html
import lxml.cssselect as cssselect


def request_lianjia_url(url, method='GET', max_retries=5, retries_interval=2):
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
					  "Chrome/71.0.3578.98 Safari/537.36"
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


def get_xiaoqu_list(city='sh'):
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
			xiaoqu[district.text][subdistrict.text] = subdistrict.attrib['href']

		time.sleep(1.0)

	return xiaoqu


def get_xiaoqu_info_in_subdistict(subdistrict_url):
	info = dict()
	h = request_lianjia_url(subdistrict_url)
	info['total_xiaoqu_number'] = int(h.find_class('total fl')[0].cssselect('span')[0].text)
	total_pages = eval(h.find_class('page-box house-lst-page-box')[0].attrib['page-data'])['totalPage']
	info['subdistric_xiaoqu'] = dict()
	for i in range(1, total_pages + 1):
		if i == 1:
			url = subdistrict_url
		else:
			url = subdistrict_url + 'pg' + str(i) + '/'
		h = request_lianjia_url(url=url)
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
			info['subdistric_xiaoqu'][xiaoqu_id] = d
	return info


sh_xiaoqu = get_xiaoqu_list('sh')
print(sh_xiaoqu)
