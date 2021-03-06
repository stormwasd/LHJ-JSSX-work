import scrapy
import json
from Scrapy_JCWL_kjzc.items import ScrapyJcwlKjzcItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time
import re
from pybase.util import send_file


class GraspZhengceSpider(scrapy.Spider):
    name = 'grasp_zhengce'
    allowed_domains = ['www.zhengce.com']
    start_urls = [
        'https://www.zhengce.com/api/forward/news/GetNewsList?pageindex=1&pagesize=20&area=RegisterArea_HDDQ_Jiangsu_NanJin&dept=&searchKey=%E5%BB%BA%E6%9D%90&areaType=false']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        info_dict = json.loads(response.text)['data']
        # content =
        for i in info_dict:
            url = 'https://www.zhengce.com/api/forward/news/GetNewsDetail?mainId=' + \
                i['mainID']
            req = scrapy.Request(
                url=url,
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = i['title']
            issue_time = i['publishTime'].split('T')[0]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"issue_time": issue_time})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        issue_time = response.meta['issue_time'].split()[0]
        content = json.loads(response.text)['data']['content']
        content_imgs = re.findall(r'src="(.*?).JPG"', content, re.DOTALL)
        imgs = []
        if len(content_imgs) >= 1:
            for index, value in enumerate(
                    content_imgs[:len(content_imgs) - 1]):
                img_title = title + str(index) + '.jpg'
                res = send_file(
                    img_title,
                    value + '.JPG',
                    self.config.get('send_url'),
                    self.headers)
                if res['code'] == 1:
                    content = content.replace(
                        value + '.JPG', res['data']['url'])
                    imgs.append(res['data']['url'])
                else:
                    self.logger.info(f'???????????? {value}.JPG ??????????????????????????????{res}')
            content_img = ','.join(imgs)
        else:
            content_img = None
        # print('content_imgs:', content_imgs)
        item = ScrapyJcwlKjzcItem()
        item['news_id'] = news_id  # id???url?????????)
        item['category'] = '????????????'  # ??????
        item['sub_category'] = '??????????????????'  # ????????????
        item['information_categories'] = '??????????????????'  # ????????????
        item['content_url'] = response.url  # ????????????
        item['title'] = title  # ??????
        item['issue_time'] = issue_time  # ????????????
        item['title_image'] = None  # ????????????
        item['information_source'] = '?????????'  # ?????????
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
        item['images'] = content_img  # ????????????
        item['phone'] = None  # ????????????
        item['source'] = None  # ??????
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_zhengce'])
