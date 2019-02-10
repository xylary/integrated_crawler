import os
import time, datetime
import requests, re
from lxml import html
import lxml.cssselect as cssselect


url = 'https://www.mgstage.com/search/search.php?search_word=&search_shop_id=nanpatv&is_monthly=1&page=1&sort=new&list_cnt=120&disp_type=thumb'
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "cookie": 'save_image=7VVBbsIwEHzNHqkSWxQ4kkBv7alwtTaJI1s1dhQbEL9nDWlULjQCVUIV0ihZT3bWs5cJJHNgye%2FgOdJLtbIGvgDGgL15iW2p%2'
              'BuKlUQ3w7iC8co3QFTVbtA2GHbBX3FBD5l0bIi33PaW92DgblDnQh7SnjfZBlDZ2p9EFA76EgX4vvVea7k9Kg96f7RfBEkHPUSVr3JpAJ487KbS'
              'tnSiMK79uv%2B8n7pQ%2FAv7BCs81%2F2LN56jHxzj7WL3DeAFLDlPCvCsy3hWz9HN976I8L7YhuBipQzK2kkZ8C04Zm5ONCU2hf0nH3xr0NCFm'
              '%2FXD5SYLXBUc%3D; PHPSESSID=2lvffp8j6v0hfkjv5q9ihcbek4; uuid=55537ff4a0f6e5bc8e16bef485dc8c96; coc=1; adc=1;'
              ' __ulfpc=201902102300495948; _ga=GA1.2.572761413.1549810854; _gid=GA1.2.552974713.1549810854'
}
r = requests.request('GET', url, headers=headers)
h = html.fromstring(r.content)
last_page_button = h.find_class('pager_search_bottom')[0].cssselect('p > a')[-1]
last_page_button.attrib['href']
