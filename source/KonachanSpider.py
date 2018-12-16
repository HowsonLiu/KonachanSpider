# Copyright: Copyright(c) 2018
# Created on 2018 - 12 - 16
# Author: HowsonLiu
# Version 1.0
# Title: Konachan爬虫

import requests
import os
import configparser
import pyperclip
import re
from bs4 import BeautifulSoup
import datetime

# 这次简单一点算了

img_name_style = r'{id}.jpg'
save_path = r'D:/KonachanSpider'
ini_path = r'./KonachanSpider.ini'
default_ini = '''[setting]
;默认保存路径
save_path={save_path}
'''
headers = {
    'Referer': 'http://konachan.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}


def CreateDefaultIni():
    global ini_path, save_path
    ini_file = open(ini_path, 'w', encoding='utf-8')
    ini_file.write(default_ini.format(save_path=save_path))
    ini_file.close()
    if not os.path.exists(save_path):
        os.mkdir(save_path)

def LoadIni():
    global save_path, ini_path
    if os.path.exists(ini_path):
        cfg = configparser.ConfigParser()
        cfg.read(ini_path, encoding='utf-8')
        if not os.path.exists(cfg['setting']['save_path']):
            CreateDefaultIni()
        else:
            save_path = cfg['setting']['save_path']
    else:
        CreateDefaultIni()

def CheckUrl(target_url):
    if not target_url or target_url == '':
        return False
    if re.compile(r'^(http://|https://)?konachan\.(com|net)/post/show/\d+').search(target_url) is None:
        return False
    return True

def GetHTMLResponse(target_url):
    try:
        target_html_res = requests.get(target_url, headers=headers)
        if str(target_html_res.status_code) != '200':
            print(target_url + '连接失败, 状态码: ' + str(target_html_res.status_code))
            return None
    except:
        # 远程主机关闭连接
        print(target_url + '连接失败, 请翻墙')
        return None
    return target_html_res

def GetImageName(soup):
    id_str = soup.find(text=re.compile('^Id: \d+'))
    if id_str is not None:
        name = re.compile('\d+').search(id_str).group()

    else:
        name = datetime.datetime.now().strftime('%Y/%m/%d %H-%M-%S')
    return img_name_style.format(id=name)

def GetImageHrefAndInfo(soup):
    # tag = soup.find('a', attrs={'class': 'original-file-changed'})
    tag = soup.find(lambda m_tag: m_tag.name == 'a' and m_tag.get('class') == ['original-file-changed'] or m_tag.get('class') == ['original-file-unchanged'])    # 精准匹配
    href = None
    info = None
    if tag is not None:
        href = tag['href']
        info = re.compile('\(.+\)').search(tag.text).group()
    return href, info

def Crawl(img_main_url):
    img_main_res = GetHTMLResponse(img_main_url)
    if img_main_res is None:
        return -1
    img_main_soup = BeautifulSoup(img_main_res.text, 'lxml')
    img_name = GetImageName(img_main_soup)
    if os.path.exists(save_path + '/' + img_name):
        print(img_name + ' 已存在')
        return 1
    img_href, img_info = GetImageHrefAndInfo(img_main_soup)
    if img_info is not None:
        print('正在下载 ' + img_name + img_info)
    else:
        print('正在下载 ' + img_name)
    if img_href is None:
        print('找不到')
        return -1
    img_href_res = GetHTMLResponse(img_href)
    if img_href_res is None:
        return -1
    img_file = open(save_path + '/' + img_name, 'wb')
    img_file.write(img_href_res.content)
    img_file.close()
    return 0

LoadIni()
print('请复制如下网页吧')
print('R18(com): https://konachan.com/post/show/275374/all_male-aqua_eyes-blonde_hair-borr-close-go_robot')
print('Normal(net): https://konachan.net/post/show/275374/all_male-aqua_eyes-blonde_hair-borr-close-go_robot')
while True:
    print('按enter开始, 按f结束')
    if input() == 'f':
        break
    print('正在处理...')
    input_url = pyperclip.paste()
    if not CheckUrl(input_url):
        print('ERROR URL: ' + input_url)
        continue
    if Crawl(input_url) != -1:
        os.startfile(save_path)
