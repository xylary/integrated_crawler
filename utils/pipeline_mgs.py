import os
import time, datetime
import requests, re
import bs4


url = 'https://www.mgstage.com/search/search.php?search_word=&search_shop_id=nanpatv&is_monthly=1&page=1&sort=new&list_cnt=120&disp_type=thumb'

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'cookie': 'adc=1'
}

r = requests.request('GET', url, headers=headers)
h = bs4.BeautifulSoup(r.content, 'lxml')
print(h.prettify())
