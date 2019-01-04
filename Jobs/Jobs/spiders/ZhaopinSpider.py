# -*- coding: utf-8 -*-
import scrapy


class ZhaopinspiderSpider(scrapy.Spider):
    name = 'ZhaopinSpider'
    allowed_domains = ['www.zhaopin.com']
    start_urls = ['http://www.zhaopin.com/']

    def parse(self, response):
        pass
