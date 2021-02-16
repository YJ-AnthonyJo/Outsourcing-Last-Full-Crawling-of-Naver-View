import requests
from pathlib import Path
import ast

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver import ActionChains
from multiprocessing import Process
import multiprocessing
import json
import pprint
from urllib import parse
import time

def find_index(data, target):
    res = []
    lis = data
    while True:
        try:
            res.append(lis.index(target) + (res[-1] + 1 if len(res) != 0 else 0))
            lis = data[res[-1] + 1:]
        except:
            break
    return res


def view(keyword, driver):
    keyword = '{}'.format(keyword)
    driver.get("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
    driver.implicitly_wait(time_to_wait=0.3)
    while True:
        last = driver.find_element_by_xpath('//*[@id="footer"]')
        action = ActionChains(driver)
        action.move_to_element(last).perform()
        driver.implicitly_wait(time_to_wait=0.3)
        height = driver.execute_script("return $(document).height()")
        print(height)
        time.sleep(3)

    li = driver.find_element_by_xpath('//li[@class="bx _svp_item"]')
    li = driver.execute_script("return arguments[0].parentNode;", li)
    html = li.get_attribute('innerHTML')
    soup = bs(html, 'html.parser')
    urlS = [k.attrs['href'] for k in soup.find_all(attrs={'class': 'api_txt_lines total_tit'})]
driver_path = "..\\ROOT\\Programming\\AssociatedFiles\\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('lang=ko_KR')
driver = webdriver.Chrome(str(driver_path), chrome_options=chrome_options)  # 드라이버 설정
view('김포', driver)