import scrapy
from Scrapy_DS_kjzc.items import ScrapyDsKjzcItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import json


class GraspSpolicySpider(scrapy.Spider):
    name = 'grasp_spolicy'
    allowed_domains = ['www.spolicy.com']
    start_urls = ['http://www.spolicy.com/']
    config = get_project_settings()
    headers = {
        'Proxy-Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://www.spolicy.com',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'JSESSIONID=FE9B8AAF80673AD5924D82AE540F2CF7'}

    def start_requests(self):
        for i in range(1, 2):
            url = "http://www.spolicy.com/info_api/policyinfoSearchController/searchEsPolicyinfo"
            payload = {
                'pageNum': str(i),
                'pageSize': '20',
                'word': '雕塑',
                'policyType': '6',
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

        item = ScrapyDsKjzcItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '雕塑产业'  # 行业子类
        item['information_categories'] = '国家科技政策'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '产业政策大数据平台'  # 网站名
        item['content'] = content  # 内容
        item['author'] = None  # 作者
        item['attachments'] = None  # 附件
        item['area'] = None  # 地区
        item['address'] = None  # 地址
        item['tags'] = None  # 标签
        item['sign'] = '51'  # 个人编号
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 爬取时间
        item['cleaning_status'] = 0
        item['images'] = None  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = source  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_spolicy'])
