import scrapy
from Scrapy_JCWL_zcdt.items import ScrapyJcwlZcdtItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import re
import json


class GraspSpolicySpider(scrapy.Spider):
    name = 'grasp_spolicy'
    allowed_domains = ['www.spolicy.com/']
    start_urls = [
        'http://www.spolicy.com/search?keyword=%E5%BB%BA%E6%9D%90&type=0']
    config = get_project_settings()
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://www.spolicy.com',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'JSESSIONID=1215E0F6CFDE501C0BB445ACAFD28496'}
    space = set()

    def start_requests(self):
        for i in range(1, 2):
            url = "http://www.spolicy.com/info_api/policyinfoSearchController/searchEsPolicyinfo"
            payload = {
                'city': '-1',
                'department': '0',
                'downtown': '-1',
                'garden': '0',
                'industry': '-1',
                'pageNum': str(i),
                'pageSize': '20',
                'policyType': '5',
                'province': '-1',
                'sorttype': '1',
                'type': '1',
                'wholews': '1',
            }
            req = scrapy.Request(
                url=url,
                callback=self.parse,
                method='POST',
                body=json.dumps(payload),
                dont_filter=True,
                headers=self.headers)
            yield req

    def parse(self, response):
        info_dict = json.loads(response.text)
        data = info_dict['data']['rows']
        for i in data:
            detail_url = 'http://www.spolicy.com/info_api/policyInfo/getPolicyInfo?id=' + \
                i.get('id')
            req = scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            time = i.get('time')
            source = i.get('releaseOrganization')
            req.meta.update({'news_id': news_id})
            req.meta.update({'time': time})
            req.meta.update({'source': source})
            yield req

    def parse_detail(self, response):
        data = json.loads(response.text)['data']['rows']
        title = data.get('title')
        if title not in self.space:
            self.space.add(title)
            content = data.get('content')
            news_id = response.meta["news_id"]
            time = response.meta['time']
            source = response.meta['source']
            item = ScrapyJcwlZcdtItem()

            item['news_id'] = news_id  # id???url?????????)
            item['category'] = '????????????'  # ??????
            item['sub_category'] = '??????????????????'  # ????????????
            item['information_categories'] = '??????????????????'  # ????????????
            item['content_url'] = response.url  # ????????????
            item['title'] = title  # ??????
            item['issue_time'] = time  # ????????????
            item['title_image'] = None  # ????????????
            item['information_source'] = '???????????????????????????'  # ?????????
            item['content'] = content  # ??????
            item['author'] = None  # ??????
            item['attachments'] = None  # ??????
            item['area'] = None  # ??????
            item['address'] = None  # ??????
            item['tags'] = None  # ??????
            item['sign'] = '51'  # ????????????
            item['update_time'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')  # ????????????
            item['cleaning_status'] = 0
            item['images'] = None  # ????????????
            item['phone'] = None  # ????????????
            item['source'] = source  # ??????
            self.logger.info(item)
            yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_spolicy'])
