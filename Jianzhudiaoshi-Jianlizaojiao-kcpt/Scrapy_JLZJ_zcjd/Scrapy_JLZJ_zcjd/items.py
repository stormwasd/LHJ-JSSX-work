# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyJlzjZcjdItem(scrapy.Item):
    # 1.id(url哈希值)
    news_id = scrapy.Field()
    # 2.行业
    category = scrapy.Field()
    # 3.行业子类
    sub_category = scrapy.Field()
    # 4.咨询类别
    information_categories = scrapy.Field()
    # 5.链接地址
    content_url = scrapy.Field()
    # 6.标题
    title = scrapy.Field()
    # 7.发布时间
    issue_time = scrapy.Field()
    # 8.标题图片
    title_image = scrapy.Field()
    # 9.网站名
    information_source = scrapy.Field()
    # 10.来源
    source = scrapy.Field()
    # 11.作者
    author = scrapy.Field()
    # 12.内容
    content = scrapy.Field()
    # 13.文章图片
    images = scrapy.Field()
    # 14.附件
    attachments = scrapy.Field()
    # 15.地区
    area = scrapy.Field()
    # 16.地址
    address = scrapy.Field()
    # 17.标签
    tags = scrapy.Field()
    # 18.个人编号
    sign = scrapy.Field()
    # 19.爬取时间
    update_time = scrapy.Field()
    # 20.清洗位   0 : 未清洗  1 ： 清洗过
    cleaning_status = scrapy.Field()
    # 21.联系方式
    phone = scrapy.Field()
