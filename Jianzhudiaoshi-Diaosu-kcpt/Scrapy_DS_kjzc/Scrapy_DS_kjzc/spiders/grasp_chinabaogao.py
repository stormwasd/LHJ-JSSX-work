import scrapy
from scrapy.utils import request
from Scrapy_DS_kjzc.items import ScrapyDsKjzcItem
from datetime import datetime
from scrapy.utils.project import get_project_settings
from pybase.util import send_file


class GraspChinabaogaoSpider(scrapy.Spider):
    name = 'grasp_chinabaogao'
    allowed_domains = ['www.chinabaogao.com']
    start_urls = ['http://www.chinabaogao.com/search?cid=zhengce&word=%E9%9B%95%E5%A1%91']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    config = get_project_settings()

    def parse(self, response):
        detail_url_list = response.xpath(
            "//h3[@class='media__title']/a/@href").extract()
        pub_time_list = response.xpath(
            "//div[@class='media__info flex-center-y']/span[@class='time mr-16']/text()").extract()
        tags_list = response.xpath(
            "//div[@class='media__info flex-center-y']/a/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request(
                url='http:' + detail_url_list[i],
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time_list[i]})
            req.meta.update({'tag': tags_list[i]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        tag = response.meta['tag']
        content_judge = ''.join(response.xpath(
            "//div[@class='cb-article__body mb-32']/div[last()]").extract())
        if '更多好文每日分享，欢迎关注公众号' in content_judge:
            content = ''.join(response.xpath(
                '//div[@class="cb-article__body mb-32"]/div[last()]/preceding-sibling::*').extract())
        else:
            content = ''.join(
                response.xpath('//div[@class="cb-article__body mb-32"]').extract())

        title = response.xpath(
            "//h1[@class='cb-article__title w-100p']/text()").extract_first()
        content_img_list = response.xpath(
            "//div[@class='cb-article__content flex-fluid']/div[@class='cb-article__body mb-32']/div/img/@src").extract()
        if len(content_img_list) >= 1 and content_img_list[-1].endswith('png'):
            content_img_list.pop(-1)
        if content_img_list:
            upload_img_list = []
            for index, value in enumerate(content_img_list):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    'http:' + value,
                    self.config.get('send_url'))
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    upload_img_list.append(res['data']['url'])
                else:
                    self.logger.info(f"图片{value}上传失败,返回值{res}")
            imgs = ','.join(upload_img_list)
        else:
            imgs = None

        item = ScrapyDsKjzcItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '雕塑产业'
        item['information_categories'] = '国家科技政策'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '观研报告网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = imgs
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = tag
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinabaogao'])
