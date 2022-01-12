import scrapy
from Scrapy_JLZJ_zscq.items import ScrapyJlzjZscqItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json


class Grasp1633Spider(scrapy.Spider):
    name = 'grasp_1633'
    allowed_domains = ['www.1633.com']
    start_urls = [
        'https://www.1633.com/patent/0/0/1/?keyword=%E7%9B%91%E7%90%86%E9%80%A0%E4%BB%B7']

    def parse(self, response):
        detail_url_list = response.xpath(
            "//a[@class='com-dbl clearfix']/@href").extract()
        title_list = response.xpath(
            "//div[@class='com-dib content']/h6[@class='u-font-20 ellipsis']/text()").extract()
        zhuanli_list = response.xpath(
            "//div[@class='com-dib content']/p[@class='u-m-t-25']/span[@class='dark-gray']/text()").extract()
        for i in range(len(detail_url_list)):
            url = detail_url_list[i]
            req = scrapy.Request(
                url='https://www.1633.com/' + url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = title_list[i]
            zhuanli = zhuanli_list[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'title': title})
            req.meta.update({'zhuanli': zhuanli})
            yield req
        next_url = response.xpath(
            "//div[@class='page']/a[last()]/@href").extract_first()
        # if next_url:
        #     req = scrapy.Request(url='https://www.1633.com/' + next_url, callback=self.parse, dont_filter=True)
        #     yield req

    def parse_detail(self, response):
        zhuanli = response.meta['zhuanli']
        title = response.meta['title']
        news_id = response.meta['news_id']
        content = ''.join(response.xpath(
            "//div[@class='pat-zscdr']/p[1]").extract())
        tag = response.xpath("//span[2]/b/text()").extract_first()

        item = ScrapyJlzjZscqItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '监理造价产业'
        item['information_categories'] = '知识产权交易平台'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = datetime.now().strftime(
            '%Y-%m-%d')
        item['title_image'] = None
        item['information_source'] = '科易网'
        item['content'] = content
        item['author'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = tag
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['images'] = None
        item['patent_number'] = zhuanli
        item['source'] = None
        self.logger.info(item)
        # yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_1633'])

