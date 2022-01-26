import scrapy
from Scrapy_YCCY_cxlm.items import ScrapyYccyCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspEastobaccoSpider(scrapy.Spider):
    name = 'grasp_ahgrrb'
    allowed_domains = ['www.ahgrrb.com']
    # start_urls = ['http://www.eastobacco.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    def start_requests(self):
        url = "http://www.ahgrrb.com/html/detail/20200825/200825075821582.html"
        req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
        news_id = request.request_fingerprint(req)
        req.meta.update({'news_id': news_id})
        yield req
    def parse(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@class='cont-item1']/h2/text()").extract_first()
        issue_time = response.xpath("//span[@class='item1-time']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='cont-item2']").extract())

        item = ScrapyYccyCxlmItem()
        item['news_id'] = news_id
        item['category'] = '食品饮料'
        item['sub_category'] = '烟草产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '安徽工人日报-皖工网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_ahgrrb'])