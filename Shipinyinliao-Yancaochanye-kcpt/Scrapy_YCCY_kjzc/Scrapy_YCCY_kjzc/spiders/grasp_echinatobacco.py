import scrapy
from scrapy.utils import request
from Scrapy_YCCY_kjzc.items import ScrapyYccyKjzcItem
from datetime import datetime
from scrapy.utils.project import get_project_settings
from pybase.util import send_file


class GraspEchinatobaccoSpider(scrapy.Spider):
    name = 'grasp_echinatobacco'
    allowed_domains = ['www.echinatobacco.com']
    start_urls = ['http://www.echinatobacco.com/html/site27/zwkx/index.html']
    config = get_project_settings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    # def start_requests(self):
    #     for i in range(2, 3):
    #         url = f"http://www.echinatobacco.com/html/site27/zhgl/index_{i}.html"
    #         req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
    #         yield req

    def parse(self, response):
        url_list = response.xpath("//ul[@class='gylist']/li/em/a/@href").extract()
        pub_time_list = response.xpath("//ul[@class='gylist']/li/span/text()").extract()
        title_list = response.xpath("//ul[@class='gylist']/li/em/a/text()").extract()
        for i in range(len(url_list)):
            req = scrapy.Request(url='http://www.echinatobacco.com' + url_list[i], callback=self.parse_detail, dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            issue_time =  pub_time_list[i]
            title = title_list[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': issue_time})
            req.meta.update({'title': title})
            yield req


    def parse_detail(self, response):
        news_id = response.meta['news_id']
        issue_time = response.meta['issue_time']
        title = response.meta['title']
        content = ''.join(response.xpath("//div[@class='scrap_detail_text']").extract())
        content_imgs = response.xpath("//div[@class='scrap_detail_text']//img/@src").extract()
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, 'http://www.echinatobacco.com' + value, self.config.get('send_url'),
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

        item = ScrapyYccyKjzcItem()
        item['news_id'] = news_id
        item['category'] = '食品饮料'
        item['sub_category'] = '烟草产业'
        item['information_categories'] = '国家科技政策'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '中国烟草资讯网'
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
    cmd.execute(['scrapy', 'crawl', 'grasp_echinatobacco'])


