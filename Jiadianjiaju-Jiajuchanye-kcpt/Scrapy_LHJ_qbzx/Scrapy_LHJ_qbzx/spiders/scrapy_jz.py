import scrapy
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from Scrapy_LHJ_qbzx.items import ScrapyLhjQbzxItem
from datetime import datetime



class ScrapyJzSpider(scrapy.Spider):
    name = 'scrapy_jz'
    allowed_domains = ['www.jz97.net']
    start_urls = ['http://www.jz97.net/e/search/result/?searchid=222']
    config = get_project_settings()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def parse(self, response):
        global title_img_url
        url_list = response.xpath("//li[@class='infinitescroll_li']/div[@class='article_text']/dl/dt/a/@href").extract()
        title_list = response.xpath("//li[@class='infinitescroll_li']/div[@class='article_text']/dl/dt/a/text()").extract()
        pub_time_list = response.xpath("//li[@class='infinitescroll_li']/div[@class='article_text']/div[@class='info']/span[1]/text()").extract()
        for i in range(len(url_list)):
            title_img = response.xpath(f"//li[@class='infinitescroll_li'][{i + 1}]/div[@class='article_img']/a/img/@src").extract()
            if title_img:
                title_img_url = title_img[0]
                img_name = title_list[i] + '.jpg'
                res = send_file(img_name, title_img_url, self.config.get('send_url'), self.headers)
                if res['code'] == 1:
                    title_img_url = res['data']['url']
                else:
                    self.logger.info(f'标题图片 {title_img[0]} 上传失败，返回数据：{res}')
            else:
                title_img_url = None
            detail_url = url_list[i]
            title = title_list[i]
            pub_time = str(datetime.now().year) + '-' + pub_time_list[i]
            req = scrapy.Request(url=detail_url, callback=self.detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.meta.update({'title': title})
            req.meta.update({'pub_time': pub_time})
            req.meta.update({'title_img_url': title_img_url})
            yield req

        # next_url = response.xpath("//div[@class='pagebar']/a[@class='next']/@href").extract_first()
        # if next_url:
        #     yield scrapy.Request(url='http://www.jz97.net/' + next_url, callback=self.parse, dont_filter=True)
    def detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        title_img_url = response.meta['title_img_url']
        source = response.xpath("//div[@class='info']/span[2]/text()").extract_first().split('：')[1]
        content = response.xpath("//div[@class='article_content']").extract_first()
        content_img_list = response.xpath("//div[@class='article_content']/p/img/@src").extract()
        content_img = []
        if content_img_list:
            for index, value in enumerate(content_img_list):
                img_name = title + str(index) + '.jpg'
                res = send_file(img_name, value, self.config.get('send_url'), self.headers)
                if res['code'] == 1:
                    content.replace(value, res['data']['url'])
                    content_img.append(res['data']['url'])
                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')
            images = ','.join(content_img)
        else:
            images = None
        item = ScrapyLhjQbzxItem()
        item['news_id'] = news_id
        item['category'] = '家电家居'
        item['sub_category'] = '家具产业'
        item['information_categories'] = '新闻资讯'
        item['content_url'] = response.url
        item['title'] = title  # 标题
        item['issue_time'] = pub_time  # 发布时间
        item['title_image'] = title_img_url  # 标题图片
        item['information_source'] = '家具在线'  # 网站名
        item['content'] = content  # 新闻的内容
        item['source'] = source  # 来源
        item['author'] = None
        item['attachments'] = None  # 附件
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '51'
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0  #
        item['images'] = images
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd

    cmd.execute(['scrapy', 'crawl', 'scrapy_jz'])

