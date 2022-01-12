import scrapy
from Scrapy_JCWL_cxlm.items import ScrapyJcwlCxlmItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file


class GraspChinaddSpider(scrapy.Spider):
    name = 'grasp_chinadd'
    allowed_domains = ['www.chinadd.cn']
    start_urls = [
        'https://www.chinadd.cn/news/search.php?catid=0&kw=%E5%BB%BA%E6%9D%90%E8%81%94%E7%9B%9F']
    config = get_project_settings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }

    def parse(self, response):
        # print(response.text)
        detail_url = response.xpath(
            "//div[@class='dd-news-list cf js-news-list']/dl/dd/h2/a/@href").extract()
        # title_list = response.xpath("")
        for u in detail_url:
            req = scrapy.Request(
                url=u,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath(
            "//div[@class='dd-ad-structure']/h1[@class='biaoti']/text()").extract_first()
        issue_time = response.xpath(
            "//p[@class='dd-source']/span[1]/text()").extract_first().split(' ')[0]
        content = ''.join(response.xpath(
            "//div[@class='js_Virgo']|//div[@class='js_Cancer']|//div[@class='js_Leo']|//div[@class='js_Taurus']").extract())
        content_image = response.xpath(
            "//div[@class='Virgo']/div[@class='js_Virgo']/p/img/@src").extract()
        if content_image != []:
            imgs = list()
            for index, value in enumerate(content_image):
                image_name = title + str(index) + '.jpg'
                res = send_file(
                    image_name,
                    value,
                    self.config.get('send_url'),
                    headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    imgs.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片上传失败，返回内容{res}')

            content_images = ','.join(imgs)
        else:
            content_images = None

        item = ScrapyJcwlCxlmItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '建材物料产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['title_image'] = None
        item['information_source'] = '顶墙网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = content_images
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
    cmd.execute(['scrapy', 'crawl', 'grasp_chinadd'])
