import scrapy
from Scrapy_SCGY_cxlm.items import ScrapyScgyCxlmItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspStonebuySpider(scrapy.Spider):
    name = 'grasp_stone139_all'
    allowed_domains = ['www.stone139.com']
    start_urls = ['http://www.stone139.com/news/search-htm-kw-%E8%81%94%E7%9B%9F.html']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }


# def start_requests(self):
    #     url = self.start_urls[0]
    #     req = scrapy.Request(url, callback=self.parse, dont_filter=True)
    #     news_id = request.request_fingerprint(req)
    #     req.meta.update({'news_id': news_id})
    #     yield req

    def parse(self, response):
        # news_id = response.meta['news_id']
        # title = response.xpath("//div[@class='col-xs-9 news-col-xs-9-800']/h1[@id='title']/text()").extract_first()
        # content = ''.join(response.xpath("//div[@class='content']").extract())
        detail_ulr_list = response.xpath("//div[@class='text-list']/h3[@class='news-tit2']/a/@href").extract()
        pub_time_list = response.xpath("//div[@class='time']/span[@class='time_ico']/text()").extract()
        for i in range(len(detail_ulr_list)):
            detail_url = detail_ulr_list[i]
            req = scrapy.Request(detail_url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time_list[i]})
            yield req
    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time'].split(" ")[0]
        content = ''.join(response.xpath("//div[@class='content']").extract())
        title = response.xpath("//h1[@id='title']/text()").extract_first()
        content_imgs = response.xpath("//div[@id='article']//@src").extract()
        if content_imgs:
            content_img_list = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    value,
                    self.config.get('send_url'),
                    headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    content_img_list.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')
            imgs = ','.join(content_img_list)
        else:
            imgs = None

        item = ScrapyScgyCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '石材工业产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '石材网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_stone139_all'])
