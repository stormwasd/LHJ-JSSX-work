import scrapy
from Scrapy_LHJ_cxgh.items import ScrapyLhjCxghItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspChinayiguiSpider(scrapy.Spider):
    name = 'grasp_home_fang'
    allowed_domains = ['www.home.fang.com']
    start_urls = ['https://home.fang.com/news/tag1401/']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_url_list = response.xpath("//div[@id='newslist']/ul/font/a/@href").extract()
        for i in range(len(detail_url_list)):
            detail_url = 'https:' + detail_url_list[i]
            req = scrapy.Request(url=detail_url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req
        # next_url = response.xpath("//div[@class='page_al mt0 mb4']/p/a[last()]/@href").extract()
        # if next_url:
        #     yield scrapy.Request(url='https://home.fang.com/' + next_url[-1], callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        global content_imgs
        news_id = response.meta['news_id']
        # title_img = response.meta['title_img']
        title = response.xpath("//div[@class='news']/h1/text()").extract_first()
        pub_time = response.xpath("//div[@class='news_tools']/text()").extract_first()[:10]
        source = ''.join(re.findall(r'[\u4e00-\u9fa5]', ''.join(response.xpath("//div[@class='news_tools']/text()").extract()), re.DOTALL))
        content = ''.join(response.xpath('//div[@class="news_cont"]').extract())
        content_img_list = response.xpath("//div[@id='news_replace']/p/img/@src").extract()
        content_img = []
        if len(content_img_list) >= 1:
            for index, value in enumerate(content_img_list):
                if value.startswith('http'):
                    upload_url = value
                else:
                    upload_url = 'http:' + value
                content_img_name = title + str(index) + '.jpg'
                res = send_file(content_img_name, upload_url, self.config.get('send_url'), self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    content_img.append(res['data']['url'])
                    content_imgs = ','.join(content_img)
                else:
                    self.logger.info(f'标题图片 {value} 上传失败，返回数据：{res}')
        else:
            content_imgs = None



        item = ScrapyLhjCxghItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = None
        item['source'] = source
        item['author'] = None
        item['content'] = content
        item['images'] = content_imgs
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = '家具技术'
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item

    if __name__ == '__main__':
        import scrapy.cmdline as cmd
        cmd.execute(['scrapy', 'crawl', 'grasp_home_fang'])
