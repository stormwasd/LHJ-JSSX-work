import scrapy
from Scrapy_CCY_zcdt.items import ScrapyCcyZcdtItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import json
from pybase.util import send_file


class GraspPuercnSpider(scrapy.Spider):
    name = 'grasp_puercn'
    allowed_domains = ['www.puercn.com']
    start_urls = ['http://www.puercn.com/']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
    config = get_project_settings()

    def start_requests(self):
        for i in range(1, 2):
            url = f"https://www.puercn.com/news/zhengce/p{i}/"
            req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
            yield req

    def parse(self, response):
        detail_url_list = response.xpath("//div[@class='inner']/ul/h3/a/@href").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request('https://www.puercn.com' + detail_url_list[i], callback=self.parse_detail,
                                 dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req


    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@class='card-body']/h1/text()").extract_first()
        issue_time = response.xpath("//span[@class='mr-2']/time/text()").extract_first().split()[0].replace('年', '-').replace('月', '-').replace('日', '')
        content = ''.join(response.xpath("//div[@class='entry-content mt-3']").extract())
        content_imgs = response.xpath("//div[@class='entry-content mt-3']//img/@src").extract()
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                if value.startswith("https"):
                    res = send_file(img_title, value, self.config.get('send_url'),
                                    headers=self.headers)
                else:
                    res = send_file(img_title, 'https://www.puercn.com' + value, self.config.get('send_url'),
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

        item = ScrapyCcyZcdtItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '食品饮料'  # 行业
        item['sub_category'] = '茶产业'  # 行业子类
        item['information_categories'] = '科技政策动态'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = issue_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '普洱茶网'  # 网站名
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
        item['images'] = imgs  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_puercn'])
