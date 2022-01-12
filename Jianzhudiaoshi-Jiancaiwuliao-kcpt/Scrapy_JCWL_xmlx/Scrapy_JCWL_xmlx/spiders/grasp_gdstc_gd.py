import json
import scrapy
from Scrapy_JCWL_xmlx.items import ScrapyJcwlXmlxItem


class GraspGdstcGdSpider(scrapy.Spider):
    name = 'grasp_gdstc_gd'
    allowed_domains = ['sjfb.gdstc.gd.gov.cn']
    start_urls = ['http://sjfb.gdstc.gd.gov.cn/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }


    def start_requests(self):
        for i in range(1, 2):
            url = f'http://sjfb.gdstc.gd.gov.cn/sjfb/api/project/listProjectInitial?size=10&current={i}&projectName=%E5%BB%BA%E6%9D%90'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
            yield req


    def parse(self, response):
        jso = json.loads(response.text)['data']['records']
        for i in jso:
            project_name = i.get('projectName')
            business_type = i.get('businessType')
            undertaking_unit = i.get('undertakeUnit')
            psn_name = i.get('projectLeader')
            data_source = '广东省科学技术厅'
            status = 1
            cleaning_status = 0
            sign = '51'
            region = '广东省'
            country = '中国'
            indic_name = '建材物料产业'
            issue_time = i.get('beginYear') + '-12-16'

            item = ScrapyJcwlXmlxItem()
            item['business_type'] = business_type
            item['undertaking_unit'] = undertaking_unit
            item['psn_name'] = psn_name
            item['data_source'] = data_source
            item['status'] = status
            item['cleaning_status'] = cleaning_status
            item['sign'] = sign
            item['region'] = region
            item['country'] = country
            item['indic_name'] = indic_name
            item['pro_name'] = project_name
            item['issue_time'] = issue_time
            self.logger.info(item)
            yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_gdstc_gd'])