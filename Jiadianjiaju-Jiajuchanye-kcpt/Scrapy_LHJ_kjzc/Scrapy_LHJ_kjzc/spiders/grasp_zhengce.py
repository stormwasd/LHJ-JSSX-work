import scrapy
from scrapy.utils import request
from Scrapy_LHJ_kjzc.items import ScrapyLhjKjzcItem
from datetime import datetime


class GraspZhengceSpider(scrapy.Spider):
    name = 'grasp_zhengce'
    allowed_domains = ['http://zhengce.new.chinabaogao.com']
    start_urls = ['http://www.chinabaogao.com/search?cid=zhengce&word=%E5%AE%B6%E5%85%B7']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }


    def start_requests(self):
        for i in range(1, 2):
            url = f"http://www.chinabaogao.com/search?word=%E5%AE%B6%E5%85%B7&cid=zhengce&page={i}"
            req = scrapy.Request(url=url, dont_filter=True, headers=self.headers)
            yield req

    def parse(self, response):
        detail_url_list = response.xpath("//h3[@class='media__title']/a/@href").extract()
        pub_time_list = response.xpath("//div[@class='media__info flex-center-y']/span[@class='time mr-16']/text()").extract()
        tags_list = response.xpath("//div[@class='media__info flex-center-y']/a/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request(url='http:' + detail_url_list[i], callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time_list[i]})
            req.meta.update({'tag': tags_list[i]})
            yield req
    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        tag = response.meta['tag']
        content = ''.join(response.xpath('//div[@class="cb-article__body mb-32"]').extract())
        title = response.xpath("//h1[@class='cb-article__title w-100p']/text()").extract_first()

        item = ScrapyLhjKjzcItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '国家科技政策'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '观研报告网'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = tag
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        # item['patent_number'] = patent_number
        self.logger.info(item)
        yield item



if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_zhengce'])







