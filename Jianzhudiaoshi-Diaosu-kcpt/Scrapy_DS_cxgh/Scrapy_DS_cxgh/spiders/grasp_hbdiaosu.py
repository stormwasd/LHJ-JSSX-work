import scrapy
from Scrapy_DS_cxgh.items import ScrapyDsCxghItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re
import json


class GraspHbdiaosuSpider(scrapy.Spider):
    name = 'grasp_hbdiaosu'
    allowed_domains = ['www.hbdiaosu.cn']
    start_urls = ['http://www.hbdiaosu.cn/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    config = get_project_settings()

    def start_requests(self):
        for i in range(1, 4):
            url = f"https://www.hbdiaosu.cn/page/{i}?s=%E5%88%9B%E6%96%B0"
            req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
            yield req


    def parse(self, response):
        url_list = response.xpath("//div[@class='item-content']/h2[@class='item-title']/a/@href").extract()
        pub_time_list = response.xpath("//div[@class='item-meta']/span[@class='item-meta-li date']/text()").extract()
        for i in range(len(url_list)):
            detail_url = url_list[i]
            pub_time = pub_time_list[i].replace('年', '-').replace('月', '-').replace('日', '')
            req = scrapy.Request(detail_url, callback=self.parse_detail, dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            req.meta.update({"pub_time": pub_time})
            yield req
    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath("//h1[@class='entry-title']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='entry-content']").extract())
        content_img = response.xpath("//a[@class='j-wpcom-lightbox']/img[@class='j-lazy']/@src").extract()
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

        item = ScrapyDsCxghItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '雕塑产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = None
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
    cmd.execute(['scrapy', 'crawl', 'grasp_hbdiaosu'])