# -*- coding: utf-8 -*-
import scrapy
import re
from chardet import detect

import json
from tinydb import TinyDB, Query
from furl import furl
from Jobs.items import JobsItem

class Job51spiderSpider(scrapy.Spider):
    name = 'Job51Spider'
    allowed_domains = ['www.51job.com']
    start_urls = ['https://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20180319']
    cache_db = TinyDB('Job51Spider-cache.json')  # 缓存数据库
    allowed_cities = ['重庆', ]# '成都', '上海', '深圳', '昆明', '杭州', '贵阳', '宁波']  # 允许的城市
    F = furl('https://search.51job.com/list/120300,000000,0000,00,9,99,java,2,2.html')  # URL母版

    def parse(self, response):
        # 验证文件是否存在并能查到数据
        if not bool(self.cache_db.all()):
            print('未找到城市信息文件，正在创建......')
            self.init_city_info(response)
        # import ipdb as pdb; pdb.set_trace()
        # 迭代每一个要爬取的城市
        for city_name in self.allowed_cities:
            # 启动 爬取某个城市 第一个请求
            # import ipdb; ipdb.set_trace()
            yield self.request_city(city_name)

    def get_city_code(self, city_name):
        '''(根据城市名)获取城市代码'''
        Q = Query()
        city = self.cache_db.get(Q.name.search(city_name))
        if isinstance(city, dict):
            return city['code']
        else:
            print('未找到城市码......')

    def init_city_info(self, response):
        '''初始化城市信息'''
        encoding = detect(response.body)['encoding']
        text_data = response.body.decode(encoding, 'ignore')
        text_data1 = re.search(r'.*?=(.*?);', text_data, re.S)
        # print(text_data1)
        text_dict = json.loads(text_data1.groups()[0])
        # 新建列表（原数据格式不能用）
        dic_new_data = []
        for i in text_dict:
            dic_new_data.append({'name': text_dict[i], 'code': i})
        # 填入文件
        for x in dic_new_data:
            self.cache_db.insert(x)


    def request_city(self, city_name, page_start=0):
        '''构造 爬取某个具体的城市 的请求对象'''
        city_code = self.get_city_code(city_name)
        url_data = {
            'city_code': city_code, # 城市代码
            'zhiye': 'python',  # 职位
            'yeshu': 2  # 页数
        }
        self.F.asdict()['path']['segments'][1] = '{city_code},000000,0000,00,9,99,{zhiye},2,{yeshu}.html'.format(**url_data)

        # 要爬取的页面的URL
        url = self.F.url
        import ipdb; ipdb.set_trace()
        req = scrapy.Request(url, callback=self.parse_city, dont_filter=True)
        # 使用 meta 传递附加数据，在 callback 中可以通过 respo.meta 取得
        req.meta['city_name'] = city_name
        # print('{0}的所有{1}相关职位爬取完成！！！'.format(city_name, url_data['zhiye']))
        return req

    def parse_city(self, response):
        '''解析具体的页面'''
        # 解析json格式的响应结果
        # resp_dict = json.loads(response.body_as_unicode())
        # 总共所能爬取的条数
        # num_found = resp_dict['data']['numFound']
        # 获取当前请求的 page_start
        # page_start = response.meta['page_start']
        # 下一次请求，需要的 start 参数
        # next_start = page_start + self.PAGE_SIZE
        # import ipdb; ipdb.set_trace()
        # 判断是否有下一页
        # if next_start < num_found:
        #     # 获取当前请求的 城市名
        #     city_name = response.meta['city_name']
        #     # 发送下一页请求
        #     yield self.request_city(city_name, page_start=next_start)

        # 解析数据
        for item in response.css('#resultList .el:not(.title)'):
            # TODO: 解析数据，只取我们需要的信息

            items = JobsItem()
            # 职位名称
            items['jobName'] = item.css('.t1 a').xpath('./@title').extract_first().strip()
            # 职位链接
            items['positionURL'] = item.css('.t1 a').xpath('./@href').extract_first().strip()
            # 公司名称
            items['company'] = item.css('.t2 a').xpath('./@title').extract_first().strip()
            # 地址
            items['city'] =  item.css('.t3::text').extract_first().strip()
            # 薪资
            items['salary'] = item.css('.t4::text').extract_first().strip()
            # 开始时间
            items['startDate'] = item.css('.t5::text').extract_first().strip()
            # import ipdb; ipdb.set_trace()
            yield items