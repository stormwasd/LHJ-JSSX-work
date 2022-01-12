import scrapy
from Scrapy_JCWL_qbzx.items import ScrapyJcwlQbzxItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time


class GraspChinairnSpider(scrapy.Spider):
    name = 'grasp_chinairn'
    allowed_domains = ['www.chinairn.com']
    start_urls = [
        'https://www.chinairn.com/searchnew.aspx?search1=%E5%BB%BA%E6%9D%90&btnSeach=']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        url_list = response.xpath(
            "//div[@class='news_list relative left clearfloat']/p[@class='h1']/a/@href").extract()
        # pub_time_list = response.xpath("//div[@class='main_info right']/div[@class='pubtime left']/text()").extract()
        # tags_list = response.xapth("//p[@class='main_keywords_r']/a/text()").extract()
        for i in range(len(url_list)):
            url = 'https://www.chinairn.com' + url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            yield req
        # next_url = response.xpath("//div[@class='pagelist left clearfloat']/a[last()-1]/@href").extract_first()
        # if next_url:
        #     yield scrapy.Request(url='https://www.chinairn.com' + next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath(
            "//h1[@class='mt3']/text()").extract_first().strip()
        pub_time = response.xpath("//em[@class='time']/text()").extract_first(
        ).replace('年', '-').replace('月', '-').replace('日', '')
        information_source = response.xpath(
            "//em[2]/text()").extract_first().replace('来源：', '')
        tags = ','.join([i.strip() for i in response.xpath(
            "//p[@class='col_l irndt_kw']/a/text()").extract()])
        content = ''.join(response.xpath(
            '//dl[@class="mt3 irndt_cont"]').extract())
        content_img_list = response.xpath(
            "//dl[@class='mt3 irndt_cont']/dd[@class='mt2']//img/@src").extract()
        content_imgs = []
        if len(content_img_list) >= 1:
            for index, value in enumerate(content_img_list):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    'https://www.chinairn.com' + value,
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    content_imgs.append(res['data']['url'])

                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')
            imgs = ','.join(content_imgs)

        else:
            imgs = None

        item = ScrapyJcwlQbzxItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '建材物料产业'
        item['information_categories'] = '情报资讯'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = information_source
        item['content'] = content
        item['author'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = tags
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        item['images'] = imgs
        item['phone'] = None
        item['source'] = '中研网数据'
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinairn'])
