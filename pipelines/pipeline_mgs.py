import os
import time, datetime
import requests, re
import lxml
import bs4
import csv


def get_fanhao_info_on_mgs_page(page_url, save_csvfilename, time_interval=0.2):
    domain = 'https://www.mgstage.com'
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'cookie': 'coc=1; adc=1'
    }

    r = requests.request('GET', page_url, headers=headers)
    h = bs4.BeautifulSoup(r.content, 'lxml')
    items = h.find('ul', class_='pickup_list').find_all('li')
    for item in items:
        info = dict()
        info['src'] = domain + item.find_all('a')[0].attrs['href'] + '/'
        info['fanhao'] = info['src'].split('/')[-2]
        info['star'] = float(item.find('p', class_='review').text.replace('\n', '').replace(' ', ''))
        try:
            r_item = requests.request('GET', info['src'], headers=headers)
            h_item = bs4.BeautifulSoup(r_item.content, 'lxml')
            info['title'] = h_item.find('title').text.replace('\n', '').replace(' ', '')
            info['replays'] = int(
                h_item.find('dl', class_='playing').find('dd').text.replace('回', '').replace(',', ''))
            info['fav_cnt'] = int(
                h_item.find('li', class_='detail_fav_cnt monthly_tv_fav_cnt').text.split('\u3000')[-1].replace(',',
                                                                                                               ''))
            print('Finishing getting info of: ', info['fanhao'])
            line = info['fanhao'] + ',' + info['title'] + ',' + str(info['star']) + ',' + \
                   str(info['fav_cnt']) + ',' + str(info['replays']) + ',' + info['src'] + '\n'
            with open(save_csvfilename, 'a+', encoding='UTF-8', newline='') as csvfile:
                csvfile.write(line)
        except AttributeError as e:
            print('Error found when getting info of: ', info['fanhao'])
            print(e)
        time.sleep(time_interval)

    print('Finishing getting info on: ', page_url)
    return


def get_magnet_links_from_torrentkitty(fanhao, min_content_size=1.0):
    domain = 'https://www.torrentkitty.tv'
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    url = domain + '/search/' + fanhao + '/'
    r = requests.get(url, headers=headers)
    h = bs4.BeautifulSoup(r.content, 'lxml')
    trs = h.find('table', {'id': 'archiveResult'}).find_all('tr')[1:]
    links_to_try = []
    for tr in trs:
        details_url = domain + tr.find_all('a')[0].attrs['href']
        r1 = requests.get(details_url, headers=headers)
        h1 = bs4.BeautifulSoup(r1.content, 'lxml')
        number_of_files = int(h1.find('table', class_='detailSummary').find_all('tr')[2].find('td').text)
        contents_size = float(h1.find('table', class_='detailSummary').find_all('tr')[3].find('td').text.split(' ')[0])
        contents_size_unit = h1.find('table', class_='detailSummary').find_all('tr')[3].find('td').text.split(' ')[1]
        magnet_link = h1.find('p', class_='action').find_all('a')[1].attrs['href']
        if number_of_files < 10 and contents_size_unit == 'GB' and contents_size >= min_content_size:
            links_to_try.append(magnet_link)
    return {fanhao: links_to_try}


if __name__ == '__main__':

    base_url = 'https://www.mgstage.com/search/search.php?' \
           'search_word=&search_shop_id=shiroutotv&is_monthly=1&page={}&sort=new&list_cnt=120&disp_type=thumb'
    csvfilename = 'mgs_shiroutotv.csv'
    for i in range(4, 32):
        page_url = base_url.format(str(i))
        get_fanhao_info_on_mgs_page(page_url, csvfilename)

    '''
    fanhao = '200GANA-1928'
    print(get_magnet_links_from_torrentkitty(fanhao, min_content_size=2.0))
    '''