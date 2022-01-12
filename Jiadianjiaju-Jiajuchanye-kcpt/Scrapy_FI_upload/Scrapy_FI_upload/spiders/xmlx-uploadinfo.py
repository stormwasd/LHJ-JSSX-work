import scrapy
import pymongo
from scrapy.utils.project import get_project_settings
import requests
import logging
import json

logger = logging.getLogger(__name__)


class UploadInfo(scrapy.Spider):
    name = 'xmlx-uploadinfo'
    start_urls = []
    config = get_project_settings()

    def __init__(*args,**kwargs):
        mongo = pymongo.MongoClient(host='192.168.3.85', port=27017)
        # mongo = pymongo.MongoClient(host=self.config.get('MONGO_HOST'), port=self.config.get('MONGO_PORT'))
        db = mongo['popular_industry']  # 选择数据库
        collection = db['lhj_kcpt_xmlx']  # 获取collection
        url_info = 'http://192.168.0.11:10020/dataApp/sciencePlatform/addList/approval'
        count = 0

        # 资讯的
        for item in collection.find(filter={'cleaning_status': 0}, no_cursor_timeout=True):
            if 'issue_time' not in dict(item).keys() or item['issue_time'] == '':
                item['issue_time'] = '0-0-0'
            time_split = item['issue_time'].split('-')
            data_day = time_split[2]
            data_month = time_split[1]
            data_year = time_split[0]
            form_data = [{
                'businessType': item['business_type'],
                'country': item['country'],
                'dataSource': item['data_source'],
                "indicName": item['indic_name'],
                "issueTime": item['issue_time'],
                "proName": item['pro_name'],
                "psnName": item['psn_name'],
                "region": item['region'],
                "undertakingUnit": item['undertaking_unit'],
            }]
            # 设置重连次数
            requests.adapters.DEFAULT_RETRIES = 15
            # 设置连接活跃状态为False
            s = requests.session()
            s.keep_alive = False
            req = requests.post(url_info, headers={'Content-Type': 'application/json;charset=UTF-8'},
                                json=form_data)
            response = json.loads(req.text)
            if response['code'] != 1:
                logger.error('上传出错，返回：{}'.format(response))
                continue
            collection.update_one(filter={'_id': item['_id']}, update={'$set': {'cleaning_status': 5}})
            logger.info('{}，上传成功！！！！！！！'.format(item['pro_name']))
            count += 1

        logger.info('上传完成，共上传：{} 条数据。。。。。'.format(count))
        mongo.close()


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute('scrapy crawl xmlx-uploadinfo'.split())


