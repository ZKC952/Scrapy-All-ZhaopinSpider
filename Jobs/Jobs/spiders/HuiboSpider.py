# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy import Selector
from Jobs.items import JobsItem
from furl import furl
import dateparser

class HuibospiderSpider(scrapy.Spider):
    name = 'HuiboSpider'
    allowed_domains = ['www.huibo.com']
    start_urls = ['http://www.huibo.com/jobsearch/?params=p1&key=PHP']
    F = furl('http://www.huibo.com/jobsearch')  # URL母版
    PAGE_SIZE = 1  # 单条页数

    def parse(self, response):
        yield self.request_url()

    def request_url(self, page_num=1):
        '''构造 爬取某个具体的城市 的请求对象'''
        url_data = {
            'yeshu': page_num,  # 页数
            'zhiye': 'php'  # 职位
        }
        # furl构造新URL
        self.F.join('?params=p{yeshu}&key={zhiye}'.format(**url_data))

        # 要爬取的页面的URL
        url = self.F.url
        # import ipdb; ipdb.set_trace()
        req = scrapy.Request(url, callback=self.parse_city, dont_filter=True)
        # 使用 meta 传递附加数据，在 callback 中可以通过 respo.meta 取得
        req.meta['page_num'] = page_num
        return req

    def parse_city(self, response):
        # 去掉页面源码中的换行符，消除换行对通过xpath取 text() 的影响
        resp = Selector(None, re.sub(r'[\r\n]', '', response.body_as_unicode()), 'html')
        # 总页数
        page_sum = int(resp.css('.milpage::text').extract_first()[1:])
        # 获取当前请求的页数 page_num
        page_num = response.meta['page_num']
        if page_sum:
            # 下一次请求，需要的 num 参数
            netx_page_num = page_num + self.PAGE_SIZE
            # import ipdb; ipdb.set_trace()
            # 判断是否有下一页
            if netx_page_num <= page_sum:
                # 发送下一页请求
                yield self.request_url(page_num=netx_page_num)

        # import ipdb; ipdb.set_trace()
        for e_item in resp.css('.postIntro .postIntroL'):
            items = JobsItem()
            item = e_item.css('.postIntroL').css('.postIntroLx')
            item_a = item.css('.name .des_title')
            items['positionURL'] = item_a.xpath('./@href').extract_first()
            items['jobName'] = item_a.xpath('./text()').extract_first()
            items['salary'] = item.xpath('.//span[@class="money"]/text()').extract_first()
            items['city'] = item.xpath('.//span[@class="address"]/text()').extract_first()
            items['workingExp'] = item.xpath('.//span[@class="exp"]/text()').extract_first()
            startDate = item.xpath('.//span[@class="job_time"]/text()').extract_first()
            # 日期有可能是空 也有可能不是数字
            if startDate:
                if re.match(r'\d', startDate):
                    startDate = startDate
                else:
                    startDate = self.parse_date(startDate)
            else:
                startDate = ''
            items['startDate'] = startDate
            items['spiderName'] = self.name
            print(items)
            yield items

    def parse_date(self, job_time):
        '''格式化时间'''
        d = dateparser.parse(job_time)
        time = str(d.year)[-2:] +"/"+ str(d.month)+ "/" + str(d.day)
        if d.month < 10 and d.day < 10:
            time = str(d.year)[-2:] +"/0"+ str(d.month)+ "/0" + str(d.day)
        return  time 
        
