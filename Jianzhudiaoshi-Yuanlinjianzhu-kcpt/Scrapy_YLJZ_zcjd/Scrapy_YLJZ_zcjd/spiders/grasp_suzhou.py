import scrapy
from Scrapy_YLJZ_zcjd.items import ScrapyYljzZcjdItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json
import re


class GraspSuzhouSpider(scrapy.Spider):
    name = 'grasp_suzhou'
    allowed_domains = ['http://ylj.suzhou.gov.cn']
    start_urls = ['http://ylj.suzhou.gov.cn/szsylj/zcjd/nav_list.shtml']

    def parse(self, response):
        detail_url_lists = response.xpath(
            "//a[@class='list-item list-doit']/@href").extract()
        pub_time = response.xpath(
            "//a[@class='list-item list-doit']/span[1]/text()").extract()
        for i in range(len(detail_url_lists)):
            req = scrapy.Request(
                'http://ylj.suzhou.gov.cn' +
                detail_url_lists[i],
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time[i]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath(
            "//div[@class='a-title']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='a-con']").extract())
        source = response.xpath(
            "//div[@class='a-ly'][1]/text()").extract_first().split('：')[1]

        item = ScrapyYljzZcjdItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '园林建筑产业'  # 行业子类
        item['information_categories'] = '科技政策解读'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = pub_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '苏州市林业局'  # 网站名
        item['content'] = content  # 内容
        item['author'] = None  # 作者
        item['attachments'] = None  # 附件
        item['area'] = None  # 地区
        item['address'] = None  # 地址
        item['tags'] = None  # 标签
        item['sign'] = '51'  # 个人编号
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 爬取时间
        item['cleaning_status'] = 0
        item['images'] = None  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = source  # 来源
        self.logger.info(item)
        yield item

    if __name__ == '__main__':
        import scrapy.cmdline as cmd
        cmd.execute(['scrapy', 'crawl', 'grasp_suzhou'])
