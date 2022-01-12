import scrapy
from scrapy.utils import request
from datetime import datetime
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
import re
from Scrapy_LHJ_qbzx.items import ScrapyLhjQbzxItem


class GraspJjbdSpider(scrapy.Spider):
    name = 'grasp_jjbd'
    allowed_domains = ['www.jjbd.cn']
    start_urls = ['http://www.jjbd.cn/list/31?p=1']
    config = get_project_settings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    def parse(self, response):
        update_time_list = response.xpath("//li/span[@class='r g9']/text()").getall()
        detail_list = response.xpath("//ul[@class='tdn lh24 f14 p10 pageList']/li/a/@href").extract()
        for i in range(len(detail_list)):
            req = scrapy.Request('http://www.jjbd.cn/' + detail_list[i], callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': update_time_list[i].split(' ')[0]})
            yield req
        # next_url = response.xpath("//p[@class='Page']/a[last()]/@href").extract_first()
        # if next_url:
        #     yield scrapy.Request(url='http://www.jjbd.cn/list/31' + next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        issue_time = response.meta['issue_time']
        content_img_list = response.xpath("//div[@class='mt10 lh24 contentText'][2]//img/@src").extract()
        content = ''.join(response.xpath('//p[@class="tc articleInfo lh24 pt5 pb5"]/following-sibling::*[2]').extract())
        title = response.xpath("//h4[@class='detailTit ml10 mr10 tc pt5 pb5']/text()").extract_first()
        content_img = []
        if len(content_img_list) >= 1:
            for index, value in enumerate(content_img_list):
                content_img_name = title + str(index) + '.jpg'
                res = send_file(content_img_name, value, self.config.get('send_url'), self.headers)
                if res['code'] == 1:
                    image = res['data']['url']
                    content = content.replace(value, image)
                    content_img.append(image)
                else:
                    self.logger.info(f'文章图片 {value} 上传失败，返回数据：{res}')
            content_imgs = ','.join(content_img)
        else:
            content_imgs = None
        content = re.sub('<span style=.*?font-size:24px;color:#337FE5;".*?span>', '', content, re.DOTALL)



        item = ScrapyLhjQbzxItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '新闻资讯'
        item['content_url'] = response.url
        item['title'] = title  # 标题
        item['issue_time'] = issue_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '家具在线'  # 网站名
        item['content'] = content  # 新闻的内容
        item['source'] = None  # 来源
        item['author'] = None
        item['attachments'] = None  # 附件
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0  #
        item['images'] = content_imgs
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd

    cmd.execute(['scrapy', 'crawl', 'grasp_jjbd'])
