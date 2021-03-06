import scrapy
from Scrapy_JLZJ_zcdt.items import ScrapyJlzjZcdtItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import json


class GraspSpolicySpider(scrapy.Spider):
    name = 'grasp_spolicy'
    allowed_domains = ['www.spolicy.com']
    start_urls = [
        'http://www.spolicy.com/search?keyword=%E5%BB%BA%E6%9D%90&type=0']
    config = get_project_settings()
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://www.spolicy.com',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'JSESSIONID=7B60289F482EA96CF36583FB9AB4AE12'}

    def start_requests(self):
        for i in range(1, 2):
            url = "http://www.spolicy.com/info_api/policyinfoSearchController/searchEsPolicyinfo"
            payload = {
                'pageNum': str(i),
                'pageSize': '20',
                'word': '็็้ ไปท',
                'policyType': '0',
                'industry': '-1',
                'department': '0',
                'startTime': '',
                'endTime': '',
                'province': '-1',
                'city': '-1',
                'downtown': '-1',
                'garden': '0',
                'sorttype': '1',
                'wholews': '1',
                'type': '0'
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
        content = data.get('content')
        news_id = response.meta["news_id"]
        time = response.meta['time']
        source = response.meta['source']

        item = ScrapyJlzjZcdtItem()
        item['news_id'] = news_id  # id๏ผurlๅๅธๅผ)
        item['category'] = 'ๅปบ็ญ้้ฅฐ'  # ่กไธ
        item['sub_category'] = '็็้ ไปทไบงไธ'  # ่กไธๅญ็ฑป
        item['information_categories'] = '็งๆๆฟ็ญๅจๆ'  # ๅจ่ฏข็ฑปๅซ
        item['content_url'] = response.url  # ้พๆฅๅฐๅ
        item['title'] = title  # ๆ ้ข
        item['issue_time'] = time  # ๅๅธๆถ้ด
        item['title_image'] = None  # ๆ ้ขๅพ็
        item['information_source'] = 'ไบงไธๆฟ็ญๅคงๆฐๆฎๅนณๅฐ'  # ็ฝ็ซๅ
        item['content'] = content  # ๅๅฎน
        item['author'] = None  # ไฝ่
        item['attachments'] = None  # ้ไปถ
        item['area'] = None  # ๅฐๅบ
        item['address'] = None  # ๅฐๅ
        item['tags'] = None  # ๆ ็ญพ
        item['sign'] = '51'  # ไธชไบบ็ผๅท
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # ็ฌๅๆถ้ด
        item['cleaning_status'] = 0
        item['images'] = None  # ๆ็ซ ๅพ็
        item['phone'] = None  # ่็ณปๆนๅผ
        item['source'] = source  # ๆฅๆบ
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_spolicy'])
