import scrapy
import json
from Scrapy_JLZJ_cgzh.items import ScrapyJlzjCgzhItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
import time


class GraspNjgcttSpider(scrapy.Spider):
    name = 'grasp_njgctt'
    allowed_domains = ['www.njgctt.com']
    start_urls = [
        'http://www.njgctt.com/search/tec/?clsid=&clsmid=&jishuleixing=&transfer=&mature=&username=&q=%E7%9B%91%E7%90%86']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        detail_urls = response.xpath("//p[@class='title']/b/a/@href").extract()
        address_list = response.xpath("//span[@class='hur1']/text()").extract()
        for i in range(len(detail_urls)):
            req = scrapy.Request(
                'http://www.njgctt.com' +
                detail_urls[i],
                callback=self.parse_detail,
                dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'address': address_list[i]})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        address = response.meta['address']
        content = ''.join(response.xpath("//div[@class='dx_Dlc']").extract())
        title = response.xpath("//h1[@class='dx_Dla']/text()").extract_first()

        item = ScrapyJlzjCgzhItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '建筑雕饰'  # 行业
        item['sub_category'] = '监理造价产业'  # 行业子类
        item['information_categories'] = '科技成果转化'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = datetime.now().strftime(
            '%Y-%m-%d')  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '高淳科技成果转化平台'  # 网站名
        item['content'] = content  # 内容
        item['author'] = None  # 作者
        item['attachments'] = None  # 附件
        item['area'] = None  # 地区
        item['address'] = address  # 地址
        item['tags'] = None  # 标签
        item['sign'] = '51'  # 个人编号
        item['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 爬取时间
        item['cleaning_status'] = 0
        item['images'] = None  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_njgctt'])
