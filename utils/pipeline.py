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

cookies = 'lianjia_uuid=ff8b97a1-5321-4818-b464-32d10b329dea;' \
		  ' _smt_uid=5c4ed7c8.51da6434;' \
		  ' UM_distinctid=16893fae8986e6-0bdcd54ba90505-b781636-1fa400-16893fae8996e2;' \
		  ' _ga=GA1.2.1153017084.1548670923;' \
		  ' sensorsdata2015jssdkcross=%7B%22distinct' \
		  '_id%22%3A%22168cfcf981d396-0fd90325cc58d9-b781636-2073600-168cfcf981e53a%22%2C%22%24' \
		  'device_id%22%3A%22168cfcf981d396-0fd90325cc58d9-b781636-2073600-168cfcf981e53a%22%2C%22' \
		  'props%22%3A%7B%7D%7D; lianjia_token=2.004e6be3f737ef437d5fc6cac64f09d0de;' \
		  ' lianjia_ssid=5f67ef20-321b-446b-83bd-8c19d11fe0f0; select_city=310000;' \
		  ' all-lj=26155dc0ee17bc7dec4aa8e464d36efd; TY_SESSION_ID=abfd3d9b-362d-4d95-a935-874ff54ff654;' \
		  ' _qzjc=1; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1548670921,1549674470,1549687399,1549856046;' \
		  ' _jzqc=1; _jzqckmp=1; _gid=GA1.2.421946419.1549856048;' \
		  ' CNZZDATA1253492439=2028931286-1548666641-%7C1549865384;' \
		  ' CNZZDATA1255633284=2007666095-1548667154-%7C1549865216;' \
		  ' CNZZDATA1273627291=1755356700-1549866452-https%253A%252F%252Fsh.lianjia.com%252F%7C1549866452;' \
		  ' _jzqa=1.3744700095792172500.1548670921.1549865682.1549868681.10;' \
		  ' _jzqx=1.1549678568.1549868681.4.jzqsr=sh%2Elianjia%2Ecom|jzqct=/ershoufang/.jzqsr=sh%2' \
		  'Elianjia%2Ecom|jzqct=/xiaoqu/; CNZZDATA1254525948=1822031947-1548670360-%7C1549863767;' \
		  ' CNZZDATA1255604082=867605303-1548668608-%7C1549865110;' \
		  ' Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1549868749;' \
		  ' _qzja=1.760564005.1548670921259.1549865682118.1549868680630.1549868745410.' \
		  '1549868749497.0.0.0.141.10; _qzjb=1.1549868680630.8.0.0.0; _qzjto=13.3.0;' \
		  ' _jzqb=1.8.10.1549868681.1'


def request_lianjia_url(url, method='GET', max_retries=5, retries_interval=2, need_cookie=False, lib='lxml'):
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
					  "Chrome/71.0.3578.98 Safari/537.36"
	}
	if need_cookie:
		headers['cookie'] = cookies
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

	if lib == 'lxml':
		h = html.fromstring(response.content)
	elif lib == 'bs4':
		h = bs4.BeautifulSoup(response.content, 'lxml')
	else:
		h = response.text
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
	xiaoqu_id = xiaoqu_url.split('/')[-2]
	h = request_lianjia_url(xiaoqu_url, lib='bs4')
	try:
		info['id'] = xiaoqu_id
		info['name'] = h.find("h1", class_="detailTitle").text
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


