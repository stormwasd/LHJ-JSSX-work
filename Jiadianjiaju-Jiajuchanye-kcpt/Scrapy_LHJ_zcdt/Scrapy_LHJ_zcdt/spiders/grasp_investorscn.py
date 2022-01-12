import scrapy
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime
from Scrapy_LHJ_zcdt.items import ScrapyLhjZcdtItem
import re


class GraspAhnwSpider(scrapy.Spider):
    name = 'grasp_investorscn'
    allowed_domains = ['www.anqing.gov.cn']
    start_urls = ['http://www.investorscn.com/serch/?s=%E5%AE%B6%E5%85%B7']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_url_list = response.xpath("//div[@class='rw_right']/h2/a[@class='post_title']/@href").extract()
        pub_time_list = response.xpath("//div[@class='rw_right']/h4[@class='date-time']/span/text()").extract()
        for i in range(len(detail_url_list)):
            url = detail_url_list[i]
            req = scrapy.Request(url=url, callback=self.parse_detail, headers=self.headers, dont_filter=True)
            news_id = request.request_fingerprint(req)
            pub_time = pub_time_list[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time})
            yield req

    def parse_detail(self, response):
        global images
        news_id = response.meta['news_id']
        pub_time = response.meta['pub_time']
        title = response.xpath("//div[@class='wzwz_title']/h1/text()").extract_first()
        # source = response.xpath("//table[@class='table_suoyin']//tr[3]/td[@class='pmingcheng'][1]/text()").extract_first()
        content = ''.join(response.xpath('//div[@class="content-text"]').extract())
        content_imgs = response.xpath("//div[@class='content-text']/p/img/@src").extract()
        imgs = []
        images = ''
        if len(content_imgs) >= 1:
            for index, value in enumerate(content_imgs):
                img_name = title + str(index) + '.jpg'
                res = send_file(img_name, 'http://www.investorscn.com/' + value, self.config.get('send_url'), headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    imgs.append(res['data']['url'])
                else:
                    self.logger.info(f'文章图片 {img_name} 上传失败，返回数据：{res}')
            images = ','.join(imgs)
        else:
            images = None

        item = ScrapyLhjZcdtItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '科技政策动态'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = None
        item['source'] = None
        item['author'] = None
        item['content'] = content
        item['images'] = images
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
    cmd.execute(['scrapy', 'crawl', 'grasp_investorscn'])






