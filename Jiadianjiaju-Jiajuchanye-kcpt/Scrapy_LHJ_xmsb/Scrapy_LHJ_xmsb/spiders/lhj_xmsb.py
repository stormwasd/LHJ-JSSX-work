from datetime import datetime
import scrapy
import json
from Scrapy_LHJ_xmsb.items import ScrapyLhjXmsbItem


class LhjXmsbSpider(scrapy.Spider):
    name = 'lhj_xmsb'
    allowed_domains = ['sjfb.gdstc.gd.gov.cn']
    start_urls = ['http://sjfb.gdstc.gd.gov.cn/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }

    def start_requests(self):
        for i in range(1, 2):
            url = f'http://sjfb.gdstc.gd.gov.cn/sjfb/api/project/listPlanDeclare?size=10&current={i}&name=%E5%AE%B6%E5%85%B7'
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
            business_type = i.get('businessType')
            undertaking_unit = i.get('undertakeUnit')
            amount_declared = i.get('declaredAmount')
            data_source = '广东省科学技术厅'
            status = 1
            cleaning_status = 0
            sign = '51'
            region = '广东省'
            country = '中国'
            indic_name = '家具产业'
            issue_time = datetime.now().strftime('%Y-%m-%d')

            item = ScrapyLhjXmsbItem()
            item['business_type'] = business_type
            item['undertaking_unit'] = undertaking_unit
            item['amount_declared'] = float(amount_declared)
            item['unit'] = '万元'
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
            # yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'lhj_xmsb'])
