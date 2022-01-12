import scrapy
from Scrapy_YLZJ_qbzx.items import ScrapyYlzjQbzxItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime


class GraspChinairnSpider(scrapy.Spider):
    name = 'grasp_chinairn'
    allowed_domains = ['www.chinairn.com']
    start_urls = ['http://www.chinairn.com/']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'https://www.chinairn.com/searchnew.aspx?Keyword=%E5%9B%AD%E6%9E%97&PageId={i}'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        url_list = response.xpath("//p[@class='h1']/a/@href").extract()
        titles = response.xpath(
            "//div[@class='news_list relative left clearfloat']/p[@class='h1']/a/text()").extract()
        for i in range(len(url_list)):
            url = 'https://www.chinairn.com' + url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.xpath("//li[@class='col_l irndt_date']/em[@class='time']/text()").extract_first(
        ).replace('年', '-').replace('月', '-').rstrip('日')
        source = response.xpath(
            "//li[@class='col_l irndt_date']/em[2]/text()").extract_first().split('：')[1]
        content = ''.join(response.xpath("//dd[@class='mt2']").extract())
        content_img = response.xpath("//dd[@class='mt2']//img/@src").extract()
        if content_img:
            content_img_list = list()
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    'https://www.chinairn.com' + value,
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

        item = ScrapyYlzjQbzxItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '园林建筑产业'
        item['information_categories'] = '情报资讯'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '中研网资讯'
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
        item['source'] = source
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinairn'])
