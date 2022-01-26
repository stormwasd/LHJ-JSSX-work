from datetime import datetime
import scrapy
from scrapy.utils import request
from Scrapy_YCCY_cxgh.items import ScrapyYccyCxghItem
from pybase.util import send_file
from scrapy.utils.project import get_project_settings



class GraspEtmocSpider(scrapy.Spider):
    name = 'grasp_etmoc'
    allowed_domains = ['www.etmoc.com']
    config = get_project_settings()
    # start_urls = ['http://www.etmoc.com/']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f"http://www.etmoc.com/look/Lookmore?page={i}&Id=2080"
            req = scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                headers=self.headers)
            yield req

    def parse(self, response):
        url_list = response.xpath(
            "//div[@class='list-li']/div[@class='li-title']/a/@href").extract()
        pub_time_list = response.xpath(
            "//div[@class='li-add']/span/text()").extract()
        for i in range(len(url_list)):
            req = scrapy.Request(
                'http://www.etmoc.com/look/'+ url_list[i],
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
        title = response.xpath("//div[@class='news-title']/h3/text()").extract_first()
        content = ''.join(response.xpath("//div[@class='news-detail detail-add']").extract())
        content_imgs = response.xpath("//div[@class='detail98']/div[@class='news-detail detail-add']//img/@src").extract()
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, 'http://www.etmoc.com' + value, self.config.get('send_url'),
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

        item = ScrapyYccyCxghItem()
        item['news_id'] = news_id
        item['category'] = '食品饮料'
        item['sub_category'] = '烟草产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '烟草市场'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_etmoc'])



