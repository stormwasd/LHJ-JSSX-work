# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyDsXmsbItem(scrapy.Item):
    # news_id
    news_id = scrapy.Field()
    # 领域
    business_type = scrapy.Field()
    # 承办单位
    undertaking_unit = scrapy.Field()
    # 申报金额
    amount_declared = scrapy.Field()
    # 单位  万元
    unit = scrapy.Field()
    # 数据来源
    data_source = scrapy.Field()
    # 0:无效 1: 有效
    status = scrapy.Field()
    # 0 : 未清洗 1 ： 清洗过
    cleaning_status = scrapy.Field()
    # 14.个人编号
    sign = scrapy.Field()
    # 地区
    region = scrapy.Field()
    # 国家
    country = scrapy.Field()
    # .名称
    indic_name = scrapy.Field()
    # 标题
    pro_name = scrapy.Field()
    # 时间
    issue_time = scrapy.Field()

