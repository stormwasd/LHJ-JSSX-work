import scrapy
from Scrapy_JLZJ_cxlm.items import ScrapyJlzjCxlmItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json


class GraspChinajsbSpider(scrapy.Spider):
    name = 'grasp_chinajsb'
    allowed_domains = ['www.dlzb.com']
    config = get_project_settings()

    payload = 'moduleid=23&areaids=&exareaid=&field=0&okw=&zizhi=&catid=&search=1&kw=%E7%9B%91%E7%90%86%E8%81%94%E7%9B%9F'
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://www.dlzb.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.dlzb.com/search/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'D3z_vi-ds=cae86fdbfc3a3dc45ce5d40e33dd42df; __jsluid_s=cd66098f5c089b1de12a18233a6d8cda; Hm_lvt_c909c1510b4aebf2db610b8d191cbe91=1640939672; PHPSESSID=au8f17rk6dhuprdjhiiqv3hoj4; Hm_lpvt_c909c1510b4aebf2db610b8d191cbe91=1640940096; D3z_vi-ds=cae86fdbfc3a3dc45ce5d40e33dd42df'
    }

    def start_requests(self):
        url = 'https://www.dlzb.com/search/'
        req = scrapy.Request(
            url=url,
            callback=self.parse,
            method='POST',
            body=json.dumps(
                self.payload),
            dont_filter=True,
            headers=self.headers)
        yield req

    def parse(self, response):
        detail_url = response.xpath(
            "//ul[@class='gclist_ul listnew']/li/a[@class='gccon_title']/@href").extract()
        for i in detail_url:
            req = scrapy.Request(
                url=i,
                callback=self.parse_detail,
                dont_filter=True,
                headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@id='title']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='bg-wz']").extract())
        issue_time = response.xpath(
            "//span[@class='color_9']/text()").extract_first()

        item = ScrapyJlzjCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '监理造价产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '中国电力招标网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['phone'] = None
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinajsb'])
