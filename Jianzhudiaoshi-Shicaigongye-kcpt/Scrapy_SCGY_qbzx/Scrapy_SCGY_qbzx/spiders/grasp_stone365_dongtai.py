import scrapy
from Scrapy_SCGY_qbzx.items import ScrapyScgyQbzxItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspStone365Spider(scrapy.Spider):
    name = 'grasp_stone365_dongtai'
    allowed_domains = ['www.stone365.com']
    start_urls = ['https://www.stone365.com/news/channel-2-1.html']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    config = get_project_settings()

    # def start_requests(self):
    #     for i in range(1, 3):
    #         url = f"https://www.stone365.com/news/channel-9-{i}.html"
    #         req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
    #         yield req

    def parse(self, response):
        detail_url_list = response.xpath("//div[@class='newsd_left']/div[@class='newslistcon']/ul/li/a/@href").extract()
        pub_time = response.xpath("//div[@class='newslistcon']/ul/li/b[@class='gey']/text()").extract()
        for i in range(len(detail_url_list)):
            true_url = 'https://www.stone365.com' + detail_url_list[i]
            req = scrapy.Request(true_url, callback=self.parse_detail, dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time[i]})
            yield req
        next_page = response.xpath("//div[@class='quotes']/a[last()-1]/@href").extract_first()
        if next_page:
            u_url = 'https://www.stone365.com' + next_page
            req = scrapy.Request(u_url, callback=self.parse, dont_filter=True, headers=self.headers)
            yield req

    def parse_detail(self, response):
        pub_time = response.meta['pub_time']
        news_id = response.meta['news_id']
        title = response.xpath("//p[@class='newsname']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='newsContent']").extract())
        content_imgs = response.xpath("//div[@class='newsContent']//img/@src").extract()
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, value, self.config.get('send_url'),
                                headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    images.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片{value}上传失败,返回值{res}')
            if len(images) != 0:
                imgs = ','.join(images)
            else:
                imgs = None
        else:
            imgs = None

        item = ScrapyScgyQbzxItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '石材工业产业'
        item['information_categories'] = '情报资讯'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '365石材网'
        item['content'] = content
        item['author'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['images'] = imgs
        item['phone'] = None
        item['source'] = None
        self.logger.info(item)
        # yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_stone365_dongtai'])
