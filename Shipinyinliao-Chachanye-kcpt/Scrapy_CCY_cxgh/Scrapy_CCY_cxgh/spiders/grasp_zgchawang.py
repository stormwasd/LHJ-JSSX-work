from datetime import datetime
import scrapy
from scrapy.utils import request
from Scrapy_CCY_cxgh.items import ScrapyCcyCxghItem
from pybase.util import send_file
from scrapy.utils.project import get_project_settings


class GraspZgchawangSpider(scrapy.Spider):
    name = 'grasp_zgchawang'
    allowed_domains = ['www.zgchawang.com']
    start_urls = ['http://www.zgchawang.com/']
    config = get_project_settings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f"http://www.zgchawang.com/news/search.php?moduleid=21&spread=0&kw=%E7%A7%91%E6%8A%80%E5%88%9B%E6%96%B0&page={i}"
            req = scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                headers=self.headers)
            yield req

    def parse(self, response):
        url_list = response.xpath("//div[@class='catlist']/ul/li/a/@href").extract()
        pub_time_list = response.xpath("//div[@class='catlist']/ul/li/i/text()").extract()
        for i in range(len(url_list)):
            req = scrapy.Request(
                url_list[i],
                callback=self.parse_detail,
                dont_filter=True,
                headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': pub_time_list[i]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        issue_time = response.meta['issue_time']
        title = response.xpath("//div[@class='m3l']/h1[@id='title']/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='content']").extract())
        content_imgs = response.xpath("//div[@id='article']//img/@src").extract()
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
                    self.logger.info(f'????????????{value}????????????,?????????{res}')
            if len(images) != 0:
                imgs = ','.join(images)
            else:
                imgs = None
        else:
            imgs = None
        item = ScrapyCcyCxghItem()
        item['news_id'] = news_id
        item['category'] = '????????????'
        item['sub_category'] = '?????????'
        item['information_categories'] = '??????????????????'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '??????'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_zgchawang'])
