import scrapy
from Scrapy_JCWL_cxgh.items import ScrapyJcwlCxghItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import re


class GraspJc001Spider(scrapy.Spider):
    name = 'grasp_jc001'
    allowed_domains = ['www.news.jc001.cn']
    start_urls = ['http://news.jc001.cn/list/?sk=%BD%A8%B2%C4%B4%B4%D0%C2']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    config = get_project_settings()

    def parse(self, response):
        detail_url_list = response.xpath(
            "//div[@class='box']/ul[@class='newsList']/li/a/@href").extract()
        issue_time_list = response.xpath(
            "//div[@class='box']/ul[@class='newsList']/li/span/text()").extract()
        for i in range(len(detail_url_list)):
            detail_url = detail_url_list[i]
            req = scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            issue_time = issue_time_list[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': issue_time})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        issue_time = response.meta['issue_time']
        title = response.xpath("//h1/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='block mainCnt']//p").extract())
        content_image = response.xpath(
            "//div[@id='mainCnt']/p/img/@src").extract()
        source = response.xpath("//div[@class='desc ac']/span[1]/text()").extract_first().split('：')[1] if '：' in response.xpath(
            "//div[@class='desc ac']/span[1]/text()").extract_first() else response.xpath("//div[@class='desc ac']/span[1]/text()").extract_first()
        if len(content_image) >= 1:
            imags = []
            for index, value in enumerate(content_image):
                img_name = title + str(index) + '.jpg'
                res = send_file(img_name, value, self.config.get('send_url'))
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    imags.append(res['data']['url'])
                else:
                    self.logger.info(f'标题图片 {value} 上传失败，返回数据：{res}')
            imgs = ','.join(imags)
        else:
            imgs = None
        item = ScrapyJcwlCxghItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '建材物料产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = None
        item['source'] = source
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
    cmd.execute(['scrapy', 'crawl', 'grasp_jc001'])
