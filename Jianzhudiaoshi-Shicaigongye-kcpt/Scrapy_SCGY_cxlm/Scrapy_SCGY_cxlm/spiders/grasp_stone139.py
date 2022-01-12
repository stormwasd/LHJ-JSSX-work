import scrapy
from Scrapy_SCGY_cxlm.items import ScrapyScgyCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspStonebuySpider(scrapy.Spider):
    name = 'grasp_stone139'
    allowed_domains = ['www.stone139.com']
    start_urls = ['http://www.stone139.com/news/show-8085.html']


    def start_requests(self):
        url = self.start_urls[0]
        req = scrapy.Request(url, callback=self.parse, dont_filter=True)
        news_id = request.request_fingerprint(req)
        req.meta.update({'news_id': news_id})
        yield req

    def parse(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@class='col-xs-9 news-col-xs-9-800']/h1[@id='title']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='content']").extract())

        item = ScrapyScgyCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '石材工业产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = '2018-01-06'
        item['title_image'] = None
        item['information_source'] = '石材网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_stone139'])
