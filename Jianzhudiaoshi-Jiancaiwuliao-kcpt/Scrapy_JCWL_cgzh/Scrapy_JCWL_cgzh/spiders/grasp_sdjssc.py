import scrapy
import json
from Scrapy_JCWL_cgzh.items import ScrapyJcwlCgzhItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time


class GraspSdjsscSpider(scrapy.Spider):
    name = 'grasp_sdjssc'
    allowed_domains = ['www.sdjssc.com']
    start_urls = ['http://www.sdjssc.com/web/achievement?page=1&count=15&sort_type=1&keyword=%E5%BB%BA%E6%9D%90&pricemin=0&pricemax=999999&randomnumber=-455382.106595']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://www.sdjssc.com/web/achievement?page={i}&count=15&sort_type=1&keyword=%E5%BB%BA%E6%9D%90&pricemin=0&pricemax=999999&randomnumber=-455382.106595'
            req = scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True)
            yield req

    def parse(self, response):
        info_dict = json.loads(response.text)['data']
        for i in info_dict:
            issue_time = i['created']
            title = i['name']
            address = i['location']
            tag = i['hi_tech_field']
            detail_url = 'http://www.sdjssc.com/web/achievement/' + \
                i['record_id']
            req = scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"address": address})
            req.meta.update({"issue_time": issue_time})
            req.meta.update({"tag": tag})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        address = response.meta['address']
        issue_time = time.strftime(
            "%Y-%m-%d",
            time.localtime(
                response.meta['issue_time']))
        tag = response.meta['tag']
        content = "<div>" + \
            json.loads(response.text)['achievementinfo']['achievement_introduction'] + "</div>"
        item = ScrapyJcwlCgzhItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '??????????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = issue_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '???????????????????????????????????????'  # ?????????
        item['content'] = content  # ??????
        item['author'] = None  # ??????
        item['attachments'] = None  # ??????
        item['area'] = None  # ??????
        item['address'] = address  # ??????
        item['tags'] = tag  # ??????
        item['sign'] = '51'  # ????????????
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # ????????????
        item['cleaning_status'] = 0
        item['images'] = None  # ????????????
        item['phone'] = None  # ????????????
        item['source'] = None  # ??????
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_sdjssc'])
