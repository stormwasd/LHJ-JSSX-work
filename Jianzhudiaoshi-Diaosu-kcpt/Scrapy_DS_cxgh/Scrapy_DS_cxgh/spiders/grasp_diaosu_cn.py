import scrapy
from Scrapy_DS_cxgh.items import ScrapyDsCxghItem
from scrapy.utils import request
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from datetime import datetime


class GraspSoMydriversSpider(scrapy.Spider):
	name = 'grasp_diaosu_cn'
	# allowed_domains = ['so.mydrivers.com']
	start_urls = ['http://news.diaosu.cn/search?q=%E5%88%9B%E6%96%B0&page=1']
	config = get_project_settings()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
	}

	# def start_requests(self):
	# 	for i in range(1, 2):
	# 		url = f"https://so.mydrivers.com/news_utf8.aspx?q=%e9%9b%95%e5%a1%91&classtype=0&omid=-1&pg={i}"
	# 		req = scrapy.Request(url, callback=self.parse, dont_filter=True, headers=self.headers)
	# 		yield req

	def parse(self, response):
		detail_urls = response.xpath("//div[@class='cnl-r']/a[@class='cnl-title']/@href").extract()
		pub_time_list = response.xpath(
			"//div[@class='cnl-info clearfix']/div[@class='cnl-time fl']/text()").extract()
		for i in range(len(detail_urls)):
			req = scrapy.Request(url=detail_urls[i], callback=self.parse_detail, headers=self.headers)
			news_id = request.request_fingerprint(req)
			req.meta.update({'news_id': news_id})
			req.meta.update({'pub_time': pub_time_list[i].split(' ')[0].replace('/', '-')})
			yield req

		# next_url = response.xpath("//div[@class='news-box']/ul[@class='pagination']/li[last()]/a/@href").extract()
		# if next_url:
		# 	yield scrapy.Request(url=next_url[-1], callback=self.parse, dont_filter=True)

	def parse_detail(self, response):
		news_id = response.meta['news_id']
		pub_time = response.meta['pub_time']
		content = ''.join(response.xpath("//div[@class='s-a-content']").extract())
		title = response.xpath("//div[@class='school-article']/h1/text()").extract_first()
		content_imgs = response.xpath("//div[@class='s-a-text']/p/img/@src").extract()
		if content_imgs:
			images = list()
			for index, value in enumerate(content_imgs):
				img_title = title + str(index) + '.jpg'
				res = send_file(img_title, 'http://news.diaosu.cn' + value, self.config.get('send_url'),
								headers=self.headers)
				if res['code'] == 1:
					content = content.replace(value, res['data']['url'])
					images.append(res['data']['url'])
				else:
					self.logger.info(f'????????????{value}????????????,?????????{res}')
			if len(images) != 0:
				imgs = ','.join(images)
			else:
				imgs = None
		else:
			imgs = None

		item = ScrapyDsCxghItem()
		item['news_id'] = news_id
		item['category'] = '????????????'
		item['sub_category'] = '????????????'
		item['information_categories'] = '??????????????????'
		item['content_url'] = response.url
		item['title'] = title
		item['issue_time'] = pub_time
		item['title_image'] = None
		item['information_source'] = '?????????'
		item['content'] = content
		item['author'] = None
		item['attachments'] = None
		item['area'] = None
		item['address'] = None
		item['tags'] = None
		item['sign'] = '51'
		item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		item['cleaning_status'] = 0
		item['images'] = imgs
		item['phone'] = None
		item['source'] = None
		self.logger.info(item)
		yield item


if __name__ == '__main__':
	import scrapy.cmdline as cmd

	cmd.execute(['scrapy', 'crawl', 'grasp_diaosu_cn'])
