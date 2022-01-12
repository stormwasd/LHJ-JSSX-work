import scrapy
from Scrapy_LHJ_cgzh.items import ScrapyLhjCgzhItem
from urllib.parse import urljoin
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
import time
from datetime import datetime


class GraspNjgcttSpider(scrapy.Spider):
    name = 'grasp_njgctt'
    allowed_domains = ['www.njgctt.com']
    start_urls = ['http://www.njgctt.com/search/tec/?p=1&q=%e5%ae%b6%e5%85%b7']
    config = get_project_settings()
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://www.njgctt.com/search/tec/?p={i}&q=%e5%ae%b6%e5%85%b7'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        url_list = response.xpath("//ul/li/p[@class='title']/b/a/@href").extract()
        address_list = response.xpath("//ul/li/div[@class='xb_bba']/span[@class='hur1']/text()").extract()
        title_list = response.xpath('//div[@class="xb_bb yun_list_div"]/ul/li/p/b/a/@title').extract()
        author_list = response.xpath("//div[@class='xb_bba']/span[@class='name']/em/text()").extract()
        for i in range(len(url_list)):
            url = urljoin(response.url, url_list[i])
            title = title_list[i]
            address = address_list[i].strip()
            author = author_list[i].strip()
            req = scrapy.Request(url, callback=self.detail,dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"address": address})
            req.meta.update({"author": author})
            yield req

    def detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        address = response.meta['address']
        author = response.meta['author']
        content = response.xpath('//div[@class="xb_ae"]/following-sibling::div[2]').extract_first()
        images = response.xpath('//div[@id="showArea"]//a/@href').extract()
        img_list = []
        if len(images) != 0:
            for index, value in enumerate(images):
                if '1633.com' in value:
                    images.pop(index)
            if len(images) != 0:
                for index, value in enumerate(images):
                    content_img_name = title + str(index) + '.jpg'
                    res = send_file(content_img_name, value, self.config.get('send_url'), headers=self.headers)
                    if res['code'] == 1:
                        image = res['data']['url']
                        img_list.append(image)
                    else:
                        self.logger.info(f'标题图片 {value} 上传失败，返回数据：{res}')
                title_image = ','.join(img_list)
            else:
                title_image = None
        else:
            title_image = None

        issue_time = time.strftime('%Y-%m-%d', time.localtime())
        information_source = '高淳科技成果转化平台'
        tags = '家具技术'

        item = ScrapyLhjCgzhItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '科技成果转化'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = title_image
        item['information_source'] = information_source
        item['content'] = content
        item['author'] = author
        item['attachments'] = None
        item['area'] = None
        item['address'] = address.replace('\xa0', '')
        item['tags'] = tags
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['images'] = None
        item['phone'] = None
        item['source'] = information_source
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_njgctt'])
