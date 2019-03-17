from utils.selenium_webdriver import *


TIME_TO_WAIT = 30
login_url = 'https://pc.xuexi.cn/points/login.html?ref=https://www.xuexi.cn/'
huiyi_url = 'https://www.xuexi.cn/89acb6d339cd09d5aaf0c2697b6a3278/9a3668c13f6e303932b5e0e100fc248b.html'
shipin_url = 'https://www.xuexi.cn/4426aa87b0b64ac671c96379a3a8bd26/db086044562a57b441c24f2af1c8e101.html'


b = init_browser(login_url)

cookies = []
while True:
    time.sleep(3)
    if b.current_url != login_url:
        time.sleep(1)
        cookies = b.get_cookies()
        break

b.get('https://www.xuexi.cn/89acb6d339cd09d5aaf0c2697b6a3278/9a3668c13f6e303932b5e0e100fc248b.html')
time.sleep(1)
huiyi_handle = b.current_window_handle
huiyi_elems = b.find_elements_by_xpath('//*[@id="Chj9orckh95s00"]/div')

for i in range(0, 5):
    huiyi_elems[i].click()
    time.sleep(TIME_TO_WAIT)
    b.switch_to.window(b.window_handles[-1])
    b.close()
    b.switch_to.window(huiyi_handle)


b.execute_script("window.open('{}', 'new_window')".format(shipin_url))
b.switch_to.window(b.window_handles[-1])
shipin_handle = b.current_window_handle

shipin_elems = b.find_elements_by_xpath('//*[@id="Cd5zymfz1fzs0"]/div')

for i in range(0, 5):
    shipin_elems[i].click()
    time.sleep(TIME_TO_WAIT)
    b.switch_to.window(b.window_handles[-1])
    b.close()
    b.switch_to.window(shipin_handle)

shipin_elems[5].click()
b.switch_to.window(b.window_handles[-1])
time.sleep(3000)
b.close()
b.switch_to.window(huiyi_handle)

huiyi_elems[5].click()
b.switch_to.window(b.window_handles[-1])
time.sleep(3000)

b.quit()