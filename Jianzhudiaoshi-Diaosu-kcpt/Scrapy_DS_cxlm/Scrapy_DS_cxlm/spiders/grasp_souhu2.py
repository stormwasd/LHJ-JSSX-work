import scrapy
from Scrapy_DS_cxlm.items import ScrapyDsCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspHebnewsSpider(scrapy.Spider):
    name = 'grasp_shouhu2'
    allowed_domains = ['www.sohu.com']
    start_urls = ['https://www.sohu.com/a/39765559_148815']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    config = get_project_settings()

    def start_requests(self):
        url = self.start_urls[0]
        req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
        news_id = request.request_fingerprint(req)
        req.meta.update({'mews_id': news_id})
        yield req

    def parse(self, response):
        news_id = response.meta['mews_id']
        title = response.xpath("//div[@class='text-title']/h1/text()").extract_first().strip()
        content = ''.join(response.xpath("//article[@class='article']").extract())
        issue_time = datetime.now().strftime('%Y-%m-%d')
        content_img = response.xpath("//article[@id='mp-editor']/p/img/@src").extract()
        if content_img:
            images = list()
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, value, self.config.get('send_url'), headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    images.append(res['data']['url'])
                else:
                    self.logger.info(f"内容图片{value}上传失败,返回值{res}")
            imgs = ','.join(images)
        else:
            imgs = None

        item = ScrapyDsCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '雕塑产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '搜狐网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = imgs
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
    cmd.execute(['scrapy', 'crawl', 'grasp_shouhu2'])