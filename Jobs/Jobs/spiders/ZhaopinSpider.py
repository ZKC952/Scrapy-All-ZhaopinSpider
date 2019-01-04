# -*- coding: utf-8 -*-
import os
import json

from tinydb import TinyDB, Query
from furl import furl
from Jobs.items import JobsItem
import scrapy


class ZhaopinspiderSpider(scrapy.Spider):
    name = 'ZhaopinSpider'
    allowed_domains = ['www.zhaopin.com', 'sou.zhaopin.com', 'fe-api.zhaopin.com']
    start_urls = ['https://www.zhaopin.com/citymap']
    cache_db = TinyDB('ZhaopinSpider-cache.json')  # 缓存数据库
    allowed_cities = ['重庆', '成都', '上海', '深圳', '昆明', '杭州', '贵阳', '宁波']  ## 允许的城市
    F = furl('https://fe-api.zhaopin.com/c/i/sou?pageSize=90&kt=3')  # URL母版
    PAGE_SIZE = 90  # 分页大小

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
        # 取源码
        script_text = response.xpath('//script[text()[contains(., "__INITIAL_STATE__")]]/text()').extract_first()
        # 去收尾空格
        script_text = script_text.strip()
        # 预处理为符合json规范的数据
        script_json = script_text[script_text.index('=') + 1:]
        # 将json字符串转为字典
        script_dict = json.loads(script_json)

        '''
        # 存储取得的json, 便于调试查看
        with open('text.json', 'wt', encoding='utf-8') as f:
            json.dump(script_dict, f, indent=4, ensure_ascii=False)
        '''

        '''
        city_list = []  # 存储城市列表
        # 将字典中的城市提取到列表中，便于查找
        for ch in script_dict['cityList']['cityMapList']:
            city_list.extend(script_dict['cityList']['cityMapList'][ch])
        # 筛选出重庆，并获取城市码
        city_code = (list(filter(lambda city: city['name'] == '重庆', city_list)) or [{'code': None}])[0]['code']
        '''
        print('正在向城市信息文件中添加信息......')
        for ch in script_dict['cityList']['cityMapList']:
            for city in script_dict['cityList']['cityMapList'][ch]:
                # 将城市信息添加到tinydb数据文件
                self.cache_db.insert(city)

    def parse(self, response):
        # if not os.path.exists('ZhaopinSpider-cache.json'): # 有缺陷的失败if
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

    def request_city(self, city_name, page_start=0):
        '''构造 爬取某个具体的城市 的请求对象'''
        city_code = self.get_city_code(city_name)
        url_data = {
            'cityId': city_code,
            'kw': 'python',
            'start': page_start
        }
        # 要爬取的页面的URL
        url = self.F.copy().add(url_data).url
        # import ipdb; ipdb.set_trace()
        req = scrapy.Request(url, callback=self.parse_city, dont_filter=False)
        # 使用 meta 传递附加数据，在 callback 中可以通过 respo.meta 取得
        req.meta['city_name'] = city_name
        req.meta['page_start'] = page_start
        print('{0}的所有{1}相关职位爬取完成！！！'.format(city_name, url_data['kw']))
        return req

    def parse_city(self, response):
        '''解析具体的页面'''
        # 解析json格式的响应结果
        resp_dict = json.loads(response.body_as_unicode())
        # 总共所能爬取的条数
        num_found = resp_dict['data']['numFound']
        # 获取当前请求的 page_start
        page_start = response.meta['page_start']
        # 下一次请求，需要的 start 参数
        next_start = page_start + self.PAGE_SIZE
        # import ipdb; ipdb.set_trace()
        # 判断是否有下一页
        if next_start < num_found:
            # 获取当前请求的 城市名
            city_name = response.meta['city_name']
            # 发送下一页请求
            yield self.request_city(city_name, page_start=next_start)
        # 解析数据
        for item in resp_dict['data']['results']:
            # TODO: 解析数据，只取我们需要的信息
            items = JobsItem()
            items["jobName"] = item["jobName"]  # 招聘职位
            items["recruitCount"] = item["recruitCount"]  # 招聘人数
            items["city"] = item["city"]["display"]  # 所在城市
            items["company"] = item["company"]["name"]  # 公司名称
            items["workingExp"] = item["workingExp"]["name"]  # 工作经验
            items["eduLevel"] = item["eduLevel"]["name"]  # 要求学历
            items["positionURL"]  = item["positionURL"]  # 职位链接
            items["salary"] = item["salary"]  # 薪资
            items['spiderName'] = self.name
            # 返回每一条数据
            yield items
