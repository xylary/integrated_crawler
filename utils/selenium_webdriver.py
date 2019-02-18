# -*- coding: utf-8 -*-

import time
import copy
import numpy as np
import sqlite3
from ctypes import windll


# import Selenium framework
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as DC


# Given the record information，Return a browser containing the index page (Max trials time = 5)
def init_browser(url, headless=False, proxy=None, chrome_driver_path=r'drivers/chromedriver.exe'):

    """
    user32 = windll.user32
    gdi32 = windll.gdi32
    dc = user32.GetDC(None)
    desktop_width = gdi32.GetDeviceCaps(dc, 8)
    desktop_height = gdi32.GetDeviceCaps(dc, 10)
    browser_width = desktop_width // 2
    browser_height = desktop_height - 40
    """

    chrome_options = Options()
    chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"')
    chrome_options.add_argument("--window-size=1920x1080")
    if headless:
        chrome_options.add_argument("--headless")

    if proxy is not None:
        chrome_options.add_argument('--proxy-server=%s' % proxy)

    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
    time.sleep(1)

    """
    browser.set_window_position(x=0, y=0, windowHandle='current')
    browser.set_window_size(browser_width, browser_height, windowHandle='currentWindow')
    """

    handles = browser.window_handles
    if len(handles) > 1:
        browser.switch_to.window(handles[0])
        browser.close()
        browser.switch_to.window(handles[1])

    browser.get(url)
    time.sleep(1.0)

    return browser



