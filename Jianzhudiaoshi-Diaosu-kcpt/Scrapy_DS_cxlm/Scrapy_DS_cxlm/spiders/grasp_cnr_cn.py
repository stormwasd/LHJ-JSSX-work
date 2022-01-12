import scrapy
from Scrapy_DS_cxlm.items import ScrapyDsCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspHebnewsSpider(scrapy.Spider):
    name = 'grasp_cnr_cn'
    allowed_domains = ['m.cnr.cn']
    start_urls = ['http://m.cnr.cn/news/20151102/t20151102_520364183.html']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    def start_requests(self):
        url = self.start_urls[0]
        req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
        news_id = request.request_fingerprint(req)
        req.meta.update({'mews_id': news_id})
        yield req

    def parse(self, response):
        news_id = response.meta['mews_id']
        title = response.xpath("//div[@class='toper2']/h1/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='TRS_Editor']").extract())
        issue_time = datetime.now().strftime('%Y-%m-%d')

        item = ScrapyDsCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '雕塑产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '央广网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_cnr_cn'])