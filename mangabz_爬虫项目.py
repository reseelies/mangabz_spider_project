from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import requests
from bs4 import BeautifulSoup as bs
import time
import random


def set_driver():  # 这个函数是设置driver的，反正代码是抄的，我看不懂
    # 下面这段代码是不让模拟浏览器出来的
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options = chrome_options)
    return driver


# 设置网页为简体中文，并返回page_source
def get_source(driver, url):
    driver.get(url)
    footer = driver.find_element_by_css_selector("div.footer")
    option1 = footer.find_element_by_xpath("//a[@class='lang-option active']")
    option2 = footer.find_element_by_xpath("//a[@class='lang-option noactive']")
    if option1.text == "繁體":
        option1.click()
        option2.click()
    html = driver.page_source
    return html


# 文件存在就算了，不存在就创建
def Make_Dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


# 爬取每一章URL和名称
def get_chapt(url):
    body = {}
    driver = set_driver()
    html = get_source(driver, url)
    soup = bs(html, "html.parser")
    driver.close()
    name_div = soup.find("div", {"class":"detail-info-1"})
    body["name"] = name_div.find("p", {"class":"detail-info-title"}).text
    chapt = soup.find("div", {"class":"detail-list-form-con"})
    chapts = chapt.find_all("a")
    body["hrefs"] = []
    body["titles"] = []
    body["pages"] = []
    for chapt in chapts:
        body["hrefs"].insert(0, chapt.attrs["href"])  # "http://www.mangabz.com" + 
        title = " ".join(chapt.text.strip("").split())
        body["titles"].insert(0, title)
        page = title.split("（")[-1].split("P")[0]
        body["pages"].insert(0, int(page))
    return body


# 爬取每一章的图片
def get_pic(url, page, path):
    driver = set_driver()
    for j in range(1, page + 1):
        sleep1 = random.randint(1,2) + random.random()  # 爬每张图片之前睡1-3秒
        time.sleep(sleep1)
        url_t = url + "#ipg{}".format(j)
        driver.get(url_t)
        time.sleep(1)  # 不睡可能报错
        
#         # 下面的是纯selenium方案
#         showimage = driver.find_element_by_id("showimage")
#         img = driver.find_element_by_xpath("//img[@id='cp_image']")
#         src = img.get_attribute("src").split("?")[0]
#         img.click()  # 翻到下一页

        # 这个是soup方案
        html = driver.page_source
        soup = bs(html, "html.parser")
        showimage = soup.find("div", {"id":"showimage"})
        src = showimage.find("img", {"id":"cp_image"}).attrs["src"]
        header = {
            "Referer":"http://www.mangabz.com/",
            "User-Agent":"""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"""
        }
        img = requests.get(src, headers = header).content
        pic_path = "{}/{:0>3d}.jpg".format(path, j)
        with open(pic_path, "wb") as fo:
            fo.write(img)
    driver.close()  # 最后关闭模拟浏览器，不然吃内存


def main(url):
    start = time.time()
    body = get_chapt(url)
    name = body["name"]
    Make_Dir("./{}".format(name))
    for i, href in enumerate(body["hrefs"]):
        path = "./{}/{:0>3d}.{}".format(name, i, body["titles"][i])
        Make_Dir(path)
        url_h = "http://www.mangabz.com" + body["hrefs"][i]
        get_pic(url_h, body["pages"][i], path)
        print(body["titles"][i], "Done")
        time.sleep(5)  # 每爬完一章睡5秒
    end = time.time()
    print("{} 爬取结束，消耗时间{:.2f}s".format(name, end - start))
    input("按回车键结束……")


url = input("请输入漫画的链接：")
main(url)
