import scrapy
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from Scrapy_LHJ_zscq.items import ScrapyLhjZscqItem
from datetime import datetime
import re


class GraspYkSpider(scrapy.Spider):
    name = 'grasp_yk'
    allowed_domains = ['www.1633.com']
    start_urls = ['https://www.1633.com/patent/0/?keyword=%E5%AE%B6%E5%85%B7']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }


    def parse(self, response):
        url_list = response.xpath("//ul[@class='com-li']/li/a[@class='com-dbl clearfix']/@href").extract()  # 前面加上https://www.1633.com/
        title_list = response.xpath("//h6[@class='u-font-20 ellipsis']/text()").extract()
        patent_number_list = response.xpath("//p[@class='u-m-t-25']/span[@class='dark-gray']/text()").extract()
        title_img_list = response.xpath("//div[@class='com-dib com-img']/img/@src").extract()  # 前面加上https
        for i in range(len(url_list)):
            url = url_list[i]
            title = title_list[i]
            title_img = title_img_list[i]
            patent_number = patent_number_list[i]
            req = scrapy.Request(url='https://www.1633.com/' + url, callback=self.detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'title': title})
            req.meta.update({'patent_number': patent_number})
            req.meta.update({'title_img': title_img})
            yield req

        # next_url = response.xpath("//div[@class='page']/a[last()]/@href").extract()
        # if next_url:
        #     yield scrapy.Request(url='https://www.1633.com/' + next_url[0], callback=self.parse, dont_filter=True)


    def detail(self, response):
        global title_img_uploaded
        news_id = response.meta['news_id']
        title = response.meta['title']
        patent_number = response.meta['patent_number']
        title_img = 'https:' + response.meta['title_img']
        title_img_name = title + '.jpg'
        res = send_file(title_img_name, title_img, self.config.get('send_url'), headers=self.headers)
        if res['code'] == 1:
            title_img_uploaded = res['data']['url']
        else:
            self.logger.info(f'标题图片 {title_img} 上传失败，返回数据：{res}')
        content = response.xpath('//h3[@class="pat-process"]/preceding-sibling::p').extract()[0]
        item = ScrapyLhjZscqItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '知识产权交易'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = None
        item['title_image'] = title_img_uploaded
        item['information_source'] = None
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = '家具技术'
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['patent_number'] = patent_number
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_yk'])

