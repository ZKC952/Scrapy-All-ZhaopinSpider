# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobsItem(scrapy.Item):
    # define the fields for your item here like:
    jobName = scrapy.Field()         # 招聘职位
    recruitCount = scrapy.Field()    # 招聘人数
    city = scrapy.Field()            # 所在城市
    company = scrapy.Field()         # 公司名称
    workingExp = scrapy.Field()      # 工作经验
    eduLevel = scrapy.Field()        # 要求学历
    positionURL = scrapy.Field()     # 职位链接
    salary = scrapy.Field()          # 薪资

    spiderName = scrapy.Field()      # 爬虫名称