import scrapy
from scrapy.utils import request
from datetime import datetime
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
import re
from Scrapy_DS_zcjd.items import ScrapyDsZcjdItem


class GraspGovSpider(scrapy.Spider):
    name = 'grasp_hongtong'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    def start_requests(self):
        url = "http://www.hongtong.gov.cn/contents/11897/666872.html"
        req = scrapy.Request(
            url,
            callback=self.parse,
            dont_filter=True,
            headers=self.headers)
        news_id = request.request_fingerprint(req)
        req.meta.update({'news_id': news_id})
        yield req

    def parse(self, response):
        news_id = response.meta['news_id']
        title = response.xpath(
            "//div[@class='cont w']/h1/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='content']").extract())
        pub_time = datetime.now().strftime('%Y-%m-%d')

        item = ScrapyDsZcjdItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '雕塑产业'
        item['information_categories'] = '科技政策解读'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '洪洞县人民政府'
        item['content'] = content
        item['source'] = None
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
    cmd.execute(['scrapy', 'crawl', 'grasp_hongtong'])
