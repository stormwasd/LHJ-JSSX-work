import scrapy
from Scrapy_YLJZ_cxlm.items import ScrapyYljzCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspYuanlinSpider(scrapy.Spider):
    name = 'grasp_yuanlin'
    allowed_domains = ['http://news.yuanlin.com/']
    start_urls = ['http://http://news.yuanlin.com//']
    config = get_project_settings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://news.yuanlin.com/Search.htm?Nclass=0&KeyWords=%c1%aa%c3%cb&PageIndex={i}'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        detail_url = response.xpath(
            "//div[@class='CommentList']/ul/li/a/@href").extract()
        for i in range(len(detail_url)):
            ture_url = 'http://news.yuanlin.com' + detail_url[i]
            req = scrapy.Request(
                ture_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//span[@id='lb_title']/text()").extract_first()
        issue_time = response.xpath(
            "//span[@id='lb_time']/text()").extract_first().split()[0]
        content = ''.join(response.xpath("//div[@id='ArticleCnt']").extract())
        content_img_list = response.xpath(
            "//div[@id='ArticleCnt']//img/@src").extract()
        if content_img_list:
            imgs_list = []
            for index, value in enumerate(content_img_list):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    value,
                    self.config.get('send_url'),
                    headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    imgs_list.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片上传失败，返回值:{res}')
            imgs = ','.join(imgs_list)
        else:
            imgs = None
        source = response.xpath(
            "//span[@id='lb_comefrom']/text()").extract_first()

        item = ScrapyYljzCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '园林建筑产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '园林网'
        item['source'] = source
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
    cmd.execute(['scrapy', 'crawl', 'grasp_yuanlin'])
