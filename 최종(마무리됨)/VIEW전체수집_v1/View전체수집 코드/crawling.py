import requests 
from pathlib import Path
import ast

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver import ActionChains
from multiprocessing import Process
import multiprocessing
import json
from pprint import pprint
from urllib import parse
import time

# for ubuntu
#from pyvirtualdisplay import Display

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


def view(keyword, driver_path):
#for ubuntu
#    display = Display(visible=0, size=(1920, 1080)) 
#    display.start()
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('lang=ko_KR')
        driver = webdriver.Chrome(str(driver_path), chrome_options=chrome_options)  # 드라이버 설정
        # driver = webdriver.Chrome(driver_path) # 드라이버 설정
    except:
        return 'driver_path Error'

    keyword = '{}'.format(keyword)
    driver.get("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
    driver.implicitly_wait(time_to_wait=0.3)
    while True:
        last = driver.find_element_by_xpath('//*[@id="footer"]')
        action = ActionChains(driver)
        action.move_to_element(last).perform()
        driver.implicitly_wait(time_to_wait=0.3)
        height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(0.5)
        if len(driver.find_elements_by_xpath('//*[@class="review_loading _trigger_base"]'))==0:
            time.sleep(1)
            if len(driver.find_elements_by_xpath('//*[@class="review_loading _trigger_base"]'))==0:
                 print(keyword, "Scroll Finished, Please Check.")
                 break

    li = driver.find_element_by_xpath('//ul[@Class="lst_total _list_base"]')
    html = li.get_attribute('innerHTML')
    soup = bs(html, 'html.parser')

    Urls = [k.attrs['href'] for k in soup.find_all(attrs={'class': 'api_txt_lines total_tit'})]

    title  = [k.get_text() for k in soup.find_all(attrs={'class': 'api_txt_lines total_tit'})]
    rank = [li_.get_attribute('data-cr-rank') for li_ in li.find_elements_by_xpath('//li[@class="bx _svp_item"]')]

    date = [k.get_text() for k in soup.find_all(attrs={'class': 'sub_time sub_txt'})]
    print('Data개수 :', len(Urls), len(rank), len(title), len(date))
    driver.close()
#for ubuntu
    #display.stop()

    return [Urls, title, date, rank]
