import scrapy
from Scrapy_JCWL_zcjd.items import ScrapyJcwlZcjdItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file
import json


class GraspZgzcinfoSpider(scrapy.Spider):
    name = 'grasp_zgzcinfo'
    allowed_domains = ['www.zgzcinfo.cn']
    # start_urls = ['http://www.zgzcinfo.cn/tools/submit_ajax.ashx?action=search_article_list&category_id=0&keyWord=%E5%BB%BA%E6%9D%90']
    config = get_project_settings()
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.zgzcinfo.cn',
        'Referer': 'http://www.zgzcinfo.cn/search.html?keyword=%E5%BB%BA%E6%9D%90',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'dt_cookie_web_user=113.66.219.221; ASP.NET_SessionId=gbj5ur3jg01gry1kzdsjc454; Hm_lvt_d5a3d314ad38edb4bcb993602d6d2315=1638867844,1638867900,1639464502,1639465082; Hm_lpvt_d5a3d314ad38edb4bcb993602d6d2315=1639465082'
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f"http://www.zgzcinfo.cn/tools/submit_ajax.ashx?action=search_article_list&category_id=0&keyWord=%E5%BB%BA%E6%9D%90"
            # payload = f"curr={i}"
            payload = {
                'curr': str(i)
            }
            req = scrapy.FormRequest(
                url, callback=self.parse, formdata=payload)
            yield req

    def parse(self, response):
        # print(response.text)
        dict_info = json.loads(response.text)['dtList']
        for i in dict_info:
            title = i['title']
            add_time = i['add_time'].split('T')[0]
            detail_url = f'http://www.zgzcinfo.cn/news/show/1028-{i["channel_id"]}.html'
            req = scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'title': title})
            req.meta.update({'add_time': add_time})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        issue_time = response.meta['add_time']
        content = ''.join(response.xpath(
            "//div[@class='article-content-wrap']").extract())

        item = ScrapyJcwlZcjdItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '??????????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = issue_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '?????????????????????'  # ?????????
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
        item['source'] = None  # ??????
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_zgzcinfo'])
