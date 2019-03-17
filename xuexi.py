from utils.selenium_webdriver import *


login_url = 'https://pc.xuexi.cn/points/login.html?ref=https://www.xuexi.cn/'
huiyi_url = 'https://www.xuexi.cn/89acb6d339cd09d5aaf0c2697b6a3278/9a3668c13f6e303932b5e0e100fc248b.html'


b = init_browser(login_url)

cookies = []
while True:
    time.sleep(3)
    if b.current_url != login_url:
        time.sleep(1)
        cookies = b.get_cookies()
        break

b.get('https://www.xuexi.cn/89acb6d339cd09d5aaf0c2697b6a3278/9a3668c13f6e303932b5e0e100fc248b.html')
elems = b.find_elements_by_xpath('//*[@id="Chj9orckh95s00"]/div')
handle = b.current_window_handle

for i in range(0, 6):
    elems[i].click()
    time.sleep(2)
    b.switch_to.window(b.window_handles[-1])
    b.close()
    b.switch_to.window(handle)

b.quit()