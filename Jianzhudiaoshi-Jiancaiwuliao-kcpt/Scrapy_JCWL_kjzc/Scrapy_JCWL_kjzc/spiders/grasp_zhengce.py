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
                    self.logger.info(f'内容图片 {value}.JPG 上传失败，返回数据：{res}')
            content_img = ','.join(imgs)
        else:
            content_img = None
        # print('content_imgs:', content_imgs)
        item = ScrapyJcwlKjzcItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '建材物料产业'  # 行业子类
        item['information_categories'] = '国家科技政策'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = issue_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '政策网'  # 网站名
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
        item['images'] = content_img  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_zhengce'])
