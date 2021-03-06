import scrapy
import json
from Scrapy_JLZJ_kjzc.items import ScrapyJlzjKjzcItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time
import re
from pybase.util import send_file


class GraspChinabaogaoSpider(scrapy.Spider):
    name = 'grasp_chinabaogao'
    allowed_domains = ['www.chinabaogao.com']
    start_urls = [
        'http://www.chinabaogao.com/search?cid=zhengce&word=%E7%9B%91%E7%90%86']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_urls = response.xpath(
            "//div[@class='media__body']/h3[@class='media__title']/a/@href").extract()
        pub_times = response.xpath(
            "//span[@class='time mr-16']/text()").extract()
        tags = response.xpath(
            "//div[@class='media__body']/div[@class='media__info flex-center-y']/a/text()").extract()
        # titles = response.xpath("//h3[@class='media__title']").extract()
        for i in range(len(detail_urls)):
            req = scrapy.Request(
                url='http:' + detail_urls[i],
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            pub_time = pub_times[i]
            tag = tags[i]
            # title = titles[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time})
            req.meta.update({'tag': tag})
            # req.meta.update({'title': title})
            yield req

    def parse_detail(self, response):
        global imgs
        news_id = response.meta['news_id']
        issue_time = response.meta['pub_time']
        tag = response.meta['tag']
        # title = response.meta['title']
        title = response.xpath(
            "//h1[@class='cb-article__title w-100p']/text()").extract_first()
        # //div[@class='cb-article__body mb-32']/div[position()<last()+1]/preceding-sibling::*
        content = ''.join(response.xpath(
            "//div[@class='cb-article__body mb-32']").extract())
        content_img = response.xpath(
            "//div[@class='cb-article__body mb-32']//img/@src").extract()
        if content_img:
            content_img_list = []
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    value,
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    content_img_list.append(res['data']['url'])
                else:
                    self.logger.info(f'???????????? {value}.JPG ??????????????????????????????{res}')
            imgs = ','.join(content_img_list)
        else:
            imgs = None
        item = ScrapyJlzjKjzcItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '??????????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = issue_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '???????????????'  # ?????????
        item['content'] = content  # ??????
        item['author'] = None  # ??????
        item['attachments'] = None  # ??????
        item['area'] = None  # ??????
        item['address'] = None  # ??????
        item['tags'] = tag  # ??????
        item['sign'] = '51'  # ????????????
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # ????????????
        item['cleaning_status'] = 0
        item['images'] = imgs  # ????????????
        item['phone'] = None  # ????????????
        item['source'] = None  # ??????
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinabaogao'])
