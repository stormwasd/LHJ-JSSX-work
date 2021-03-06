import scrapy
from Scrapy_YCCY_zcdt.items import ScrapyYccyZcdtItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import json
from pybase.util import send_file




class GraspEchinatobaccoSpider(scrapy.Spider):
    name = 'grasp_echinatobacco'
    allowed_domains = ['www.echinatobacco.com']
    start_urls = ['http://www.echinatobacco.com//html/site27/zwkx/index.html']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
    config = get_project_settings()

    # def start_requests(self):
    #     for i in range(1, 2):
    #         url = f"http://www.echinatobacco.com/html/site27/zwkx/index_{i}.html"
    #         req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
    #         yield req

    def parse(self, response):
        title_list = response.xpath("//ul[@class='gylist']/li/em/a/text()").extract()
        detail_url_list = response.xpath("//ul[@class='gylist']/li/em/a/@href").extract()
        pub_time_list =  response.xpath("//ul[@class='gylist']/li/span/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request('http://www.echinatobacco.com' + detail_url_list[i], callback=self.parse_detail, dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'title': title_list[i]})
            req.meta.update({'issue_time': pub_time_list[i]})
            yield req
    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        issue_time = response.meta['issue_time']
        content = ''.join(response.xpath("//div[@class='scrap_detail_text']").extract())
        content_imgs = response.xpath("//div[@class='scrap_detail_text']//img/@src").extract()
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, 'http://www.echinatobacco.com' + value, self.config.get('send_url'),
                                headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    images.append(res['data']['url'])
                else:
                    self.logger.info(f'????????????{value}????????????,?????????{res}')
            if len(images) != 0:
                imgs = ','.join(images)
            else:
                imgs = None
        else:
            imgs = None

        item = ScrapyYccyZcdtItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = issue_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '?????????????????????'  # ?????????
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
    cmd.execute(['scrapy', 'crawl', 'grasp_echinatobacco'])


