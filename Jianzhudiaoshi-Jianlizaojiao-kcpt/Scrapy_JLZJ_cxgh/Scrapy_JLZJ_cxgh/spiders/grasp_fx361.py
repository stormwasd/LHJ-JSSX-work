import scrapy
from Scrapy_JLZJ_cxgh.items import ScrapyJlzjCxghItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspFx361Spider(scrapy.Spider):
    name = 'grasp_fx361'
    allowed_domains = ['www.fx361.com']
    start_urls = ['http://www.fx361.com/']

    def start_requests(self):
        for i in range(1, 2):
            url = f'https://api2.fx361.com/JunJiProject/JUNJI_012_001/getSearchList?bkpagesize=14&pagesize=30&keyword=%E7%9B%91%E7%90%86%E5%88%9B%E6%96%B0&pageIndex={i}&fragmentSize=150'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        jso = json.loads(response.text)
        data = jso['result']
        for i in data:
            source = i['source']
            pub_time = i['pdate']
            detail_url = 'https://www.fx361.com/page' + i['href']
            req = scrapy.Request(
                detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'source': source})
            req.meta.update({'pub_time': pub_time})
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        source = response.meta['source']
        pub_time = response.meta['pub_time']
        news_id = response.meta['news_id']
        content = ''.join(response.xpath(
            "//div[@class='article_love']/preceding-sibling::*[position()<last()-1]").extract())
        title = response.xpath(
            "//div[@class='detail_main']/h1[@id='title']/text()").extract_first()

        item = ScrapyJlzjCxghItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '监理造价产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '参考网'
        item['source'] = source
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
    cmd.execute(['scrapy', 'crawl', 'grasp_fx361'])
