import scrapy
from scrapy.utils import request
from datetime import datetime
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
import re
from Scrapy_LHJ_zcjd.items import ScrapyLhjZcjdItem


class GraspGovSpider(scrapy.Spider):
    name = 'grasp_gov'
    allowed_domains = ['www.gov.cn']
    start_urls = ['http://sousuo.gov.cn/s.htm?t=zhengce&q=%E5%AE%B6%E5%85%B7%E6%94%BF%E7%AD%96']

    def parse(self, response):
        detail_url_list = response.xpath("//ul[@class='middle_result_con show'][3]/li/a/@href").extract()
        issue_time = response.xpath(
            "//ul[@class='middle_result_con show'][3]/li/a/span[@class='date']/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request(detail_url_list[i], callback=self.parse_detail)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': issue_time[i].lstrip()})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        issue_time = response.meta['issue_time']
        title = response.xpath("//div[@class='article oneColumn pub_border']/h1/text()").extract_first().lstrip().rstrip()
        content = '<div>' + ''.join(response.xpath('//div["pages_content"]/p[position()<last()]').extract()) + '</div>'
        item = ScrapyLhjZcjdItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '科技政策解读'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '中华人民共和国中央人民政府'
        item['content'] = content
        item['source'] = '中华人民共和国中央人民政府'
        item['author'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['images'] = None
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd

    cmd.execute(['scrapy', 'crawl', 'grasp_gov'])