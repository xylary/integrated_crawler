from utils.selenium_webdriver import *


look_articles = True
watch_videos = True
headless_mode = False


TIME_TO_WAIT_ARTICLE = 30
TIME_TO_WAIT_VIDEO = 310
login_url = 'https://pc.xuexi.cn/points/login.html?ref=https://www.xuexi.cn/'
toutiao_url = 'https://www.xuexi.cn/72ac54163d26d6677a80b8e21a776cfa/9a3668c13f6e303932b5e0e100fc248b.html'
video_url = 'https://www.xuexi.cn/4426aa87b0b64ac671c96379a3a8bd26/db086044562a57b441c24f2af1c8e101.html'


# Login and get cookies
b = init_browser(login_url)
cookies = []
while True:
    time.sleep(3)
    if b.current_url != login_url:
        time.sleep(1)
        cookies = b.get_cookies()
        b.quit()
        break


b = init_browser('https://www.baidu.com', headless=headless_mode)
b.delete_all_cookies()
for cookie in cookies:
    print(cookie)
    b.add_cookie(cookie)

b.get(toutiao_url)
time.sleep(1)


print('\nStart time: ', time.ctime())

if look_articles:
    # Look articles
    huiyi_handle = b.current_window_handle
    huiyi_elems = b.find_elements_by_xpath('//*[@id="C9vbojkfmu8w00"]/div')

    for i in range(0, 5):
        huiyi_elems[i].click()
        b.switch_to.window(b.window_handles[-1])
        print('Reading article: ', b.current_url, ', time: ', time.ctime())
        for i in range(5):
            time.sleep(TIME_TO_WAIT_ARTICLE)
            b.execute_script('window.scrollBy(0, 1000)')
        b.close()
        b.switch_to.window(huiyi_handle)

    b.switch_to.window(huiyi_handle)
    huiyi_elems[5].click()
    b.switch_to.window(b.window_handles[-1])
    print('Reading article: ', b.current_url, ', time: ', time.ctime())
    for i in range(5):
        time.sleep(TIME_TO_WAIT_ARTICLE)
        b.execute_script('window.scrollBy(0, 1000)')
    time.sleep(2200)


if watch_videos:
    b.execute_script("window.open('{}', 'new_window')".format(video_url))
    b.switch_to.window(b.window_handles[-1])
    shipin_handle = b.current_window_handle
    shipin_elems = b.find_elements_by_xpath('//*[@id="Cd5zymfz1fzs0"]/div')

    for i in range(0, 6):
        shipin_elems[i].click()
        b.switch_to.window(b.window_handles[-1])
        print('Watching video: ', b.current_url, ', time: ', time.ctime())
        b.execute_script('window.scrollBy(0, 1000)')
        time.sleep(TIME_TO_WAIT_VIDEO)
        if i == 5:
            time.sleep(TIME_TO_WAIT_VIDEO * 5)
        b.close()
        b.switch_to.window(shipin_handle)

    b.close()


b.quit()