import scrapy
from Scrapy_SCGY_cxlm.items import ScrapyScgyCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspStonebuySpider(scrapy.Spider):
    name = 'grasp_stonebuy'
    allowed_domains = ['news.stonebuy.com']
    start_urls = ['http://news.stonebuy.com/2014/03/20143128928.html']


    def start_requests(self):
        url = self.start_urls[0]
        req = scrapy.Request(url, callback=self.parse, dont_filter=True)
        news_id = request.request_fingerprint(req)
        req.meta.update({'news_id': news_id})
        yield req

    def parse(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@class='detail_con']/h1/text()").extract_first()
        content = ''.join(response.xpath("//font[@face='Verdana']").extract())

        item = ScrapyScgyCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '石材工业产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = datetime.now().strftime('%Y-%m-%d')
        item['title_image'] = None
        item['information_source'] = '百石网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_stonebuy'])
