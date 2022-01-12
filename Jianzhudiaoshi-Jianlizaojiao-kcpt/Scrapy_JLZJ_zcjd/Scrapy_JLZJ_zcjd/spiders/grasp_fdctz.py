import scrapy
from Scrapy_JLZJ_zcjd.items import ScrapyJlzjZcjdItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json
import re


class GraspFdctzSpider(scrapy.Spider):
    name = 'grasp_fdctz'
    allowed_domains = ['www.fdctz.org.cn']
    start_urls = ['http://www.fdctz.org.cn/html/law/list_18_1.html']
    config = get_project_settings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://www.fdctz.org.cn/html/law/list_18_{i}.html'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        detail_urls = response.xpath(
            "//div[@class='list_cnt']/ul/li/a[@class='fl']/@href").extract()
        pub_times = response.xpath(
            "//div[@class='list_cnt']/ul/li/span[@class='fr']/text()").extract()
        for i in range(len(detail_urls)):
            ture_detail_url = 'http://www.fdctz.org.cn' + detail_urls[i]
            req = scrapy.Request(
                ture_detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            pub_time = pub_times[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time})
            yield req

    def parse_detail(self, response):
        global imgs
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath(
            "//div[@class='list']/div[@class='detail']/h1/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='detail_cnt']").extract())
        content_img = response.xpath(
            "//div[@class='detail_cnt']//img/@src").extract()
        imgs = ''
        if content_img:
            img_list = []
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    'http://www.fdctz.org.cn/' + value,
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    img_list.append(res['data']['url'])
                else:
                    self.logger.info(f"图片{value}上传失败,返回值{res}")

            imgs = ','.join(img_list)
        else:
            imgs = None

        item = ScrapyJlzjZcjdItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '监理造价产业'  # 行业子类
        item['information_categories'] = '科技政策解读'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = pub_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '中国工程监理与咨询网'  # 网站名
        item['content'] = content  # 内容
        item['author'] = None  # 作者
        item['attachments'] = None  # 附件
        item['area'] = None  # 地区
        item['address'] = None  # 地址
        item['tags'] = None  # 标签
        item['sign'] = '51'  # 个人编号
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 爬取时间
        item['cleaning_status'] = 0
        item['images'] = None  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_fdctz'])
