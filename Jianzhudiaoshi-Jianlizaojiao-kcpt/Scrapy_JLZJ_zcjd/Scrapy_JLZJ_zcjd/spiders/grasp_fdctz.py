import scrapy
from Scrapy_JLZJ_zcjd.items import ScrapyJlzjZcjdItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json
import re


class GraspFdctzSpider(scrapy.Spider):
    name = 'grasp_fdctz'
    allowed_domains = ['www.fdctz.org.cn']
    start_urls = ['http://www.fdctz.org.cn/html/law/list_18_1.html']
    config = get_project_settings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://www.fdctz.org.cn/html/law/list_18_{i}.html'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        detail_urls = response.xpath(
            "//div[@class='list_cnt']/ul/li/a[@class='fl']/@href").extract()
        pub_times = response.xpath(
            "//div[@class='list_cnt']/ul/li/span[@class='fr']/text()").extract()
        for i in range(len(detail_urls)):
            ture_detail_url = 'http://www.fdctz.org.cn' + detail_urls[i]
            req = scrapy.Request(
                ture_detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            pub_time = pub_times[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time})
            yield req

    def parse_detail(self, response):
        global imgs
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath(
            "//div[@class='list']/div[@class='detail']/h1/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='detail_cnt']").extract())
        content_img = response.xpath(
            "//div[@class='detail_cnt']//img/@src").extract()
        imgs = ''
        if content_img:
            img_list = []
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    'http://www.fdctz.org.cn/' + value,
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    img_list.append(res['data']['url'])
                else:
                    self.logger.info(f"??????{value}????????????,?????????{res}")

            imgs = ','.join(img_list)
        else:
            imgs = None

        item = ScrapyJlzjZcjdItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '??????????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = pub_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '??????????????????????????????'  # ?????????
        item['content'] = content  # ??????
        item['author'] = None  # ??????
        item['attachments'] = None  # ??????
        item['area'] = None  # ??????
        item['address'] = None  # ??????
        item['tags'] = None  # ??????
        item['sign'] = '51'  # ????????????
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # ????????????
        item['cleaning_status'] = 0
        item['images'] = None  # ????????????
        item['phone'] = None  # ????????????
        item['source'] = None  # ??????
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_fdctz'])
