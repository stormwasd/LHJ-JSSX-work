import scrapy
from scrapy.utils import request
from Scrapy_LHJ_cxlm.items import ScrapyLhjCxlmItem
from datetime import datetime
from pybase.util import send_file
from scrapy.utils.project import get_project_settings


class GraspHouseChinaSpider(scrapy.Spider):
    name = 'grasp_chinadd'
    allowed_domains = ['www.chinadd.cn']
    start_urls = ['https://www.chinadd.cn/news/search.php?catid=0&kw=%E5%AE%B6%E5%85%B7%E4%BA%A7%E4%B8%9A%E8%81%94%E7%9B%9F']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_url_list = response.xpath("//div[@class='dd-news-list cf js-news-list']/dl/dd/h2/a/@href").extract()
        # tags_list = response.xpath("//span[@class='num1-last']/div[@class='tagLeft']/a/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request(url=detail_url_list[i], callback=self.parse_detail, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            # req.meta.update({'tags': tags_list[i]})
            yield req


    def parse_detail(self, response):
        global imgs
        news_id = response.meta['news_id']
        # tag = response.meta['tags']
        title = response.xpath("//h1[@class='biaoti']/text()").extract_first()
        pub_time = response.xpath("//p[@class='dd-source']/span[1]/text()").extract_first().split(' ')[0]
        content_imgs = response.xpath("//p/img/@src").extract()[1:]
        content = ''.join(response.xpath("//p[@class='dd-lead js-lead']/following-sibling::div[1]").extract())
        # source = response.xpath("//div[@class='content-infor']/span[@class='from']/a/text()").extract_first()
        img_list = []
        if len(content_imgs) >= 1:
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, value, self.config.get('send_url'), self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    img_list.append(res['data']['url'])
            imgs = ','.join(img_list)
        else:
            imgs = None

        item = ScrapyLhjCxlmItem()

        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '创新战略联盟'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '顶墙网'
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
        # item['patent_number'] = patent_number
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinadd'])











