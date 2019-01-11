# Scrapy-All-ZhaopinSpider
爬取各大招聘网站的招聘详细信息

## 操作环境
- 操作系统：Windows
- Scrapy版本：1.5.0
- 数据库：[tinydb](https://github.com/msiemens/tinydb)、[mongoDB](https://www.mongodb.com/cn)
- 辅助技术：[furl](https://github.com/gruns/furl/blob/master/API.md)、[dateparser](https://github.com/scrapinghub/dateparser)

## 爬取信息
```
职位名称
来源站点/链接
薪资范围
地区
学历
工作经验
更多详细>
```
## 项目步骤
```
pip install tinydb furl dateparser
```
```python
# 前程无忧、智联招聘可以在主文件中添加城市或取消注释
allowed_cities = ['重庆', ]# '成都', '上海', '深圳', '昆明', '杭州', '贵阳', '宁波']  # 允许的城市
```
## 最后
>运行`run.cmd`文件即可