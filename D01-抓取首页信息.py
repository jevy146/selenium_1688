# -*- coding: utf-8 -*-
# @Time    : 2020/6/18 9:31
# @Author  : 结尾！！
# @FileName: D01-抓取首页信息.py
# @Software: PyCharm


from selenium.webdriver import ChromeOptions
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

#第一步实现对淘宝的登陆
class Chrome_drive():
    def __init__(self):
        ua = UserAgent()

        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)

        NoImage = {"profile.managed_default_content_settings.images": 2}  # 控制 没有图片
        option.add_experimental_option("prefs", NoImage)

        # option.add_argument(f'user-agent={ua.chrome}')  # 增加浏览器头部

        # chrome_options.add_argument(f"--proxy-server=http://{self.ip}")  # 增加IP地址。。

        # option.add_argument('--headless')  #无头模式 不弹出浏览器

        self.browser = webdriver.Chrome(options=option)
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        })  #去掉selenium的驱动设置

        self.browser.set_window_size(1200,768)
        self.wait = WebDriverWait(self.browser, 12)

    def get_login(self):
        url='https://www.1688.com/'

        self.browser.get(url)
        #self.browser.maximize_window()  # 在这里登陆的中国大陆的邮编
        #这里进行人工登陆。
        time.sleep(2)
        self.browser.refresh()  # 刷新方法 refres
        return


    #获取判断网页文本的内容：
    def index_page(self,page,wd):
        """
        抓取索引页
        :param page: 页码
        """
        print('正在爬取第', page, '页')


        url = f'https://s.1688.com/selloffer/offer_search.htm?keywords=%D0%A1%D0%CD%C3%AB%BD%ED%BC%D3%C8%C8%B9%F1&n=y&netType=16&beginPage={page}#sm-filtbar'
        js1 = f" window.open('{url}')"  # 执行打开新的标签页
        print(url)
        self.browser.execute_script(js1)  # 打开新的网页标签
            # 执行打开新一个标签页。
        self.browser.switch_to.window(self.browser.window_handles[-1])  # 此行代码用来定位当前页面窗口
        self.buffer()  # 网页滑动  成功切换
            #等待元素加载出来
        time.sleep(3)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#render-engine-page-container > div > div.common-pagination > div > div > div > span:nth-child(2) > input')))
            #获取网页的源代码
        html =  self.browser.page_source

        get_products(wd,html)

        self.close_window()


    def buffer(self): #滑动网页的
        for i in range(20):
            time.sleep(0.5)
            self.browser.execute_script('window.scrollBy(0,380)', '')  # 向下滑行300像素。

    def close_window(self):
        length=self.browser.window_handles
        print('length',length) #判断当前网页窗口的数量
        if  len(length) > 3:
            self.browser.switch_to.window(self.browser.window_handles[1])
            self.browser.close()
            time.sleep(1)
            self.browser.switch_to.window(self.browser.window_handles[-1])


import csv
def save_csv(lise_line):
    file = csv.writer(open("./1688_com.csv",'a',newline="",encoding="utf-8"))
    file.writerow(lise_line)

#解析网页，
from scrapy.selector import Selector
def get_products(wd,html_text):
    """
    提取商品数据
    """
    select=Selector(text=html_text)
    # 大概有47个
    items = select.xpath('//*[@id="sm-offer-list"]/div/*').extract()
    print('产品数 ',len(items))
    for i in range(1, len(items)+1):
        #详情页链接
        desc_href = select.xpath(f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="img-container"]//a/@href').extract_first()
        # 图片链接
        img_url  = select.xpath(f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="img"]/@style').extract_first()
        # 复购率
        shop_repurchase_rate = select.xpath(
            f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="desc-container"]//span[@class="shop-repurchase-rate"]/text()').extract_first()
        # title  # 标题
        title = select.xpath(
            f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="desc-container"]//div[@class="title"]//text()').extract()
        title_name=''.join(title)
        #price  #价格
        price = select.xpath(f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="desc-container"]//div[@class="price-container"]/div[@class="price"]/text()').extract_first()
        # sales_num  # 成交量
        sales_num = select.xpath(
            f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="desc-container"]//div[@class="price-container"]/div[@class="sale"]/text()').extract_first()
        #company_name  # 公司名称
        company_name = select.xpath(f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="company-name"]/a/text()').extract_first()
        #company_href  # 公司链接
        company_href = select.xpath(f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="company-name"]/a/@href').extract_first()
        #company_tag  # 公司标签
        company_tag = select.xpath(
            f'//*[@id="sm-offer-list"]/div[{i}]//div[@class="common-company-tag"]//text()').extract_first()

        all_desc=[wd,title_name,img_url,desc_href,price,sales_num,company_name,company_href,company_tag,shop_repurchase_rate]
        print(all_desc)
        save_csv(all_desc)




def main():
    """
    遍历每一页
    """
    run=Chrome_drive()
    run.get_login() #先扫码登录

    wd=['小型毛巾加热柜']
    for w in wd:

        for i in range(1, 6): #1688总计展示了6页，抓取了前5页的内容
            run.index_page(i,w)


if __name__ == '__main__':
    csv_head = 'word,title_name,img_url,desc_href,price,sales_num,company_name,company_href,company_tag,shop_repurchase_rate'.split(
        ',')
    save_csv(csv_head)
    main()