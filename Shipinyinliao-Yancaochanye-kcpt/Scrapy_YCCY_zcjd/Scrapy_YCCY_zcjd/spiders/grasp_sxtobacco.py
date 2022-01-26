import scrapy
from Scrapy_YCCY_zcjd.items import ScrapyYccyZcjdItem
from scrapy.utils import request
from scrapy.utils.project import get_project_settings
from datetime import datetime
from pybase.util import send_file


class GraspZgzcinfoSpider(scrapy.Spider):
    name = 'grasp_sxtobacco'
    allowed_domains = ['www.gxtobacco.com.cn']
    start_urls = ['http://sn.tobacco.gov.cn/zcfg/zcjd.htm']
    config = get_project_settings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse(self, response):
        detail_url_list = response.xpath("//ul[@class='ul_5']/li/a/@href").extract()
        pub_time_list = response.xpath("//span[@class='date']/text()").extract()
        for i in range(len(detail_url_list)):
            req = scrapy.Request('http://sn.tobacco.gov.cn' + detail_url_list[i].rstrip(".."), callback=self.parse_detail, dont_filter=True, headers=self.headers)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'issue_time': pub_time_list[i].replace('年', '-').replace('月', '-').replace('日', '')})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.xpath("//div[@class='tite']/h3/text()").extract_first()
        issue_time = response.meta['issue_time']
        content = ''.join(response.xpath(
            "//div[@class='content']").extract())
        content_imgs = response.xpath("//p[@class='vsbcontent_img']/img/@src").extract()
        # http://sn.tobacco.gov.cn
        if content_imgs:
            images = list()
            for index, value in enumerate(content_imgs):
                img_title = title + str(index) + '.jpg'
                res = send_file(img_title, 'http://sn.tobacco.gov.cn' + value, self.config.get('send_url'),
                                headers=self.headers)
                if res['code'] == 1:
                    content = content.replace(value, res['data']['url'])
                    images.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片{value}上传失败,返回值{res}')
            if len(images) != 0:
                imgs = ','.join(images)
            else:
                imgs = None
        else:
            imgs = None

        item = ScrapyYccyZcjdItem()
        item['news_id'] = news_id  # id（url哈希值)
        item['category'] = '食品饮料'  # 行业
        item['sub_category'] = '烟草产业'  # 行业子类
        item['information_categories'] = '科技政策解读'  # 咨询类别
        item['content_url'] = response.url  # 链接地址
        item['title'] = title  # 标题
        item['issue_time'] = issue_time  # 发布时间
        item['title_image'] = None  # 标题图片
        item['information_source'] = '中国烟草'  # 网站名
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
        item['images'] = imgs  # 文章图片
        item['phone'] = None  # 联系方式
        item['source'] = None  # 来源
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_sxtobacco'])
