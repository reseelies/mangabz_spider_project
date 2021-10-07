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

# 检验章节名称中是否有"/"，有的话需要处理掉，替换成'、'
def chack_path(file_name):
    if '/' in file_name:
        return '、'.join(file_name.split('/'))
    else:
        return file_name

# 爬取每一章URL和名称
def get_chapt(url):
    body = {}
    driver = set_driver()
    html = get_source(driver, url)
    soup = bs(html, "html.parser")
    name_div = soup.find("div", {"class":"detail-info-1"})
    body["name"] = name_div.find("p", {"class":"detail-info-title"}).text.strip()
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
    driver.close()
    return body

# 爬取每一章的图片
def get_pic(url, page, path):
    for j in range(1, page + 1):
        pic_path = "{}/{:0>3d}.jpg".format(path, j)
        if os.path.exists(pic_path):   # 这一步是用来爬取出错时再次执行用的
            continue   # 如果图片存在，那么就跳过
        driver = set_driver()
        url_t = url + "#ipg{}".format(j)
        driver.get(url_t)
        sleep1 = random.randint(1,3) + random.random()  # 爬每张图片之前睡1-4秒
        time.sleep(sleep1)
#         driver.get(url_t)
#         time.sleep(1)  # 不睡可能报错
        
#         # 下面的是纯selenium方案
#         showimage = driver.find_element_by_id("showimage")
#         img = driver.find_element_by_xpath("//img[@id='cp_image']")
#         src = img.get_attribute("src").split("?")[0]
#         img.click()  # 翻到下一页

        # 这个是soup方案
        html = driver.page_source
        soup = bs(html, "html.parser")
        driver.close()  # 最后关闭模拟浏览器，不然吃内存
        showimage = soup.find("div", {"id":"showimage"})
        src = showimage.find("img", {"id":"cp_image"}).attrs["src"]
        header = {
            "Referer":"http://www.mangabz.com/",
            "User-Agent":"""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"""
        }
        img = requests.get(src, headers = header).content
        with open(pic_path, "wb") as fo:
            fo.write(img)


def main(url):
    pics_num = 0
    start = time.time()
    body = get_chapt(url)
    name = body["name"]
    start_chapt = eval(input("请输入爬取的开始章节数(从0开始)："))
    end_chapt = eval(input("请输入爬取的结束章节数(输入0表示后续全部)："))
    if end_chapt == 0:
        href_ls = body["hrefs"][start_chapt:]
    else:
        href_ls = body["hrefs"][start_chapt:end_chapt]
    plus = int(input("请输入开始序号(无特殊需求请输入0)："))
    b = input("爬取章节为：{} - {}，是否爬取？(y/n)".format(body["titles"][start_chapt], body["titles"][end_chapt - 1]))
    if b == 'n':
        exit(0)
    Make_Dir("./{}".format(name))
    print("{} 准备完毕，开始爬取图片".format(name))
    for i, href in enumerate(href_ls, start = plus):  # 临时更改，下次使用记得恢复
        file_name = chack_path(body["titles"][start_chapt + i - plus])
        path = "./{}/{:0>3d}.{}".format(name, i, file_name)
        Make_Dir(path)
        url_h = "http://www.mangabz.com" + body["hrefs"][start_chapt + i - plus]
        try:
            get_pic(url_h, body["pages"][start_chapt + i - plus], path)
        except:
            print(body["titles"][start_chapt + i - plus], "爬取失败")
        else:
            print(body["titles"][start_chapt + i - plus], "Done")
            pics_num += body["pages"][start_chapt + i - plus]
        time.sleep(3)  # 每爬完一章睡5秒
    end = time.time()
    print("{} 爬取结束，共{}张图片，消耗时间{:.2f}s".format(name, pics_num, end - start))
    input("按回车键结束……")

url = input("请输入漫画的链接：")
main(url)
