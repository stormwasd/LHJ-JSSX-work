import scrapy
from Scrapy_YCCY_qbzx.items import ScrapyYccyQbzxItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime


class GraspEastobaccoSpider(scrapy.Spider):
    name = 'grasp_eastobacco'
    allowed_domains = ['www.eastobacco.com']
    start_urls = ['https://www.eastobacco.com/ty/node_81.html']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    config = get_project_settings()

    # def start_requests(self):
    #     for i in range(1, 2):
    #         url = f"https://www.eastobacco.com/ty/node_81_{i}.html"
    #         req = scrapy.Request(
    #             url,
    #             callback=self.parse,
    #             dont_filter=True,
    #             headers=self.headers)
    #         yield req

    def parse(self, response):
        url_list = response.xpath("//div[@class='list']/li/a/@href").extract()
        titles_list = response.xpath(
            "//div[@class='list']/li/a/text()").extract()
        issue_time_list = response.xpath(
            "//div[@class='list']/li/span/text()").extract()

        for i in range(len(url_list)):
            url = url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles_list[i]
            issue_time = issue_time_list[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"issue_time": issue_time})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        issue_time = response.meta['issue_time']
        content = ''.join(response.xpath(
            "//div[@class='mtb20 clear']").extract())
        content_imgs = response.xpath(
            "//div[@id='ContentText']//img/@src").extract()
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
                    self.logger.info(f'内容图片{value}上传失败,返回值{res}')
            if len(images) != 0:
                imgs = ','.join(images)
            else:
                imgs = None
        else:
            imgs = None
        item = ScrapyYccyQbzxItem()
        item['news_id'] = news_id
        item['category'] = '食品饮料'
        item['sub_category'] = '烟草产业'
        item['information_categories'] = '情报资讯'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '东方烟草网'
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
        item['source'] = None
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_eastobacco'])
