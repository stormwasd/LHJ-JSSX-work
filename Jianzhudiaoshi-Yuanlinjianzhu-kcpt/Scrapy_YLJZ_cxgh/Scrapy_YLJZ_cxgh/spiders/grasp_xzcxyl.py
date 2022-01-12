from datetime import datetime
import scrapy
from scrapy.utils import request
from Scrapy_YLJZ_cxgh.items import ScrapyYljzCxghItem


class GraspXzcxylSpider(scrapy.Spider):
    name = 'grasp_xzcxyl'
    allowed_domains = ['http://www.xzcxyl.com/']
    start_urls = [
        'http://www.xzcxyl.com/plus/search.php?kwtype=0&q=%E5%88%9B%E6%96%B0&submit=%E6%90%9C%E7%B4%A2']

    def parse(self, response):
        pub_time = response.xpath(
            "//div[@class='wztitle-list']/ul/li/span/text()").extract()
        detail_url = response.xpath(
            "//div[@class='wztitle-list']/ul/li/a/@href").extract()
        for i in range(len(detail_url)):
            url = 'http://www.xzcxyl.com' + detail_url[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time[i]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath(
            "//div[@class='newstext-box']/h1[@class='news-title-h1']/text()").extract_first()
        content = ''.join(response.xpath('//div[@class="newstext"]').extract())

        item = ScrapyYljzCxghItem()
        item['news_id'] = news_id
        item['category'] = '建筑雕饰'
        item['sub_category'] = '园林建筑产业'
        item['information_categories'] = '科技创新规划'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '创新园林绿化'
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = None
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
    cmd.execute(['scrapy', 'crawl', 'grasp_xzcxyl'])
