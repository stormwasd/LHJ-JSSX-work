import scrapy
import json
from Scrapy_JLZJ_kjzc.items import ScrapyJlzjKjzcItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time
import re
from pybase.util import send_file


class GraspChinabaogaoSpider(scrapy.Spider):
    name = 'grasp_chinabaogao'
    allowed_domains = ['www.chinabaogao.com']
    start_urls = [
        'http://www.chinabaogao.com/search?cid=zhengce&word=%E7%9B%91%E7%90%86']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_urls = response.xpath(
            "//div[@class='media__body']/h3[@class='media__title']/a/@href").extract()
        pub_times = response.xpath(
            "//span[@class='time mr-16']/text()").extract()
        tags = response.xpath(
            "//div[@class='media__body']/div[@class='media__info flex-center-y']/a/text()").extract()
        # titles = response.xpath("//h3[@class='media__title']").extract()
        for i in range(len(detail_urls)):
            req = scrapy.Request(
                url='http:' + detail_urls[i],
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            pub_time = pub_times[i]
            tag = tags[i]
            # title = titles[i]
            req.meta.update({'news_id': news_id})
            req.meta.update({'pub_time': pub_time})
            req.meta.update({'tag': tag})
            # req.meta.update({'title': title})
            yield req

    def parse_detail(self, response):
        global imgs
        news_id = response.meta['news_id']
        issue_time = response.meta['pub_time']
        tag = response.meta['tag']
        # title = response.meta['title']
        title = response.xpath(
            "//h1[@class='cb-article__title w-100p']/text()").extract_first()
        # //div[@class='cb-article__body mb-32']/div[position()<last()+1]/preceding-sibling::*
        content = ''.join(response.xpath(
            "//div[@class='cb-article__body mb-32']").extract())
        content_img = response.xpath(
            "//div[@class='cb-article__body mb-32']//img/@src").extract()
        if content_img:
            content_img_list = []
            for index, value in enumerate(content_img):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    value,
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    content_img_list.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片 {value}.JPG 上传失败，返回数据：{res}')
            imgs = ','.join(content_img_list)
        else:
            imgs = None
        item = ScrapyJlzjKjzcItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '监理造价产业'  # 行业子类
        item['information_categories'] = '国家科技政策'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = issue_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '观研报告网'  # 网站名
        item['content'] = content  # 内容
        item['author'] = None  # 作者
        item['attachments'] = None  # 附件
        item['area'] = None  # 地区
        item['address'] = None  # 地址
        item['tags'] = tag  # 标签
        item['sign'] = '51'  # 个人编号
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 爬取时间
        item['cleaning_status'] = 0
        item['images'] = imgs  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_chinabaogao'])
