from datetime import datetime
import scrapy
import json
from Scrapy_JLZJ_xmys.items import ScrapyJlzjXmysItem


class GraspGdstcGdGovSpider(scrapy.Spider):
    name = 'grasp_gdstc_gd_gov_jz'
    allowed_domains = ['sjfb.gdstc.gd.gov.cn']
    start_urls = ['http://sjfb.gdstc.gd.gov.cn/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://sjfb.gdstc.gd.gov.cn/sjfb/api/project/listTPlanCheck?size=10&current={i}&projectName=%E5%BB%BA%E7%AD%91'
            req = scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                headers=self.headers)
            yield req

    def parse(self, response):
        jso = json.loads(response.text)['data']['records']
        for i in jso:
            project_name = i.get('projectName')
            undertaking_unit = i.get('undertakeUnit')
            inspected = i.get('acceptanceResults')
            data_source = '广东省科学技术厅'
            status = 1
            cleaning_status = 0
            sign = '51'
            region = '广东省'
            country = '中国'
            indic_name = '监理造价产业'
            issue_time = datetime.now().strftime('%Y-%m-%d')

            item = ScrapyJlzjXmysItem()
            item['pro_name'] = project_name
            item['undertaking_unit'] = undertaking_unit
            item['data_source'] = data_source
            item['inspected'] = inspected
            item['issue_time'] = issue_time
            item['status'] = status
            item['cleaning_status'] = cleaning_status
            item['sign'] = sign
            item['region'] = region
            item['country'] = country
            item['indic_name'] = indic_name
            self.logger.info(item)
            yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_gdstc_gd_gov_jz'])
