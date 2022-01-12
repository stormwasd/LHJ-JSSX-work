import scrapy
from pybase.util import send_file
from scrapy.utils.project import get_project_settings
from Scrapy_LHJ_qbzx.items import ScrapyLhjQbzxItem
from scrapy.utils import request
from datetime import datetime
import re


class GraspJiagleSpider(scrapy.Spider):
	name = 'grasp_jiagle'
	allowed_domains = ['www.jiagle.com']
	start_urls = ['https://www.jiagle.com/jiaju_news/pinpai/1.html']
	config = get_project_settings()

	img_src_xpath = "//ul[@class='news_lb4']/li/div[@class='imgk']/a/img/@src"
	title_xpath = "//ul[@class='news_lb4']/li/div[@class='txtk']/a[@class='dbt']/text()"
	publish_time_xpath = "//ul[@class='news_lb4']/li/div[@class='txtk']/span[@class='sj']/text()"
	detail_url_xpath = "//ul[@class='news_lb4']/li/div[@class='txtk']/a/@href"
	whole_content_xpath = '//div[@class="news_bq"]/preceding-sibling::*'
	content_source_xpath = "//div[@class='d1'][1]/div[@class='news_sj']/span[@class='s1']/text()"
	max_page_xpath = "//div[@class='page clear']/ul/li/a[@class='pagenav']/text()"
	next_page_url_xpath = "//ul/li[@class='pagination-next']/a/@href"
	content_img_xpath = ""
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
	}

	def parse(self, response):
		url_list = response.xpath(self.detail_url_xpath).extract()
		title_list = response.xpath(self.title_xpath).extract()
		time_list = response.xpath(self.publish_time_xpath).extract()
		title_img_list = response.xpath(self.img_src_xpath).extract()
		for i in range(len(url_list)):
			url = url_list[i]
			issue_time = time_list[i]
			title = title_list[i]
			title_img = title_img_list[i]
			req = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
			news_id = request.request_fingerprint(req)
			req.meta.update({'news_id': news_id})
			req.meta.update({"issue_time": issue_time})
			req.meta.update({"title": title})
			req.meta.update(({"title_img": title_img}))
			yield req
		# next_page_url = response.xpath(self.next_page_url_xpath).extract()[0]
		# if next_page_url is not None:
		# 	yield scrapy.Request(next_page_url, callback=self.parse)

	def parse_detail(self, response):
		news_id = response.meta['news_id']
		issue_time = response.meta['issue_time']
		title = response.meta['title']
		tags = ','.join(response.xpath("//div[@class='news_bq']/a/span/text()").extract())
		title_img = response.meta["title_img"].rstrip('!300')
		img_name = title + '.jpg'
		res = send_file(img_name, title_img, self.config.get('send_url'), self.headers)
		if res['code'] == 1:
			image = res['data']['url']
		else:
			image = None
			self.logger.info(f'标题图片 {title_img} 上传失败，返回数据：{res}')
		content = ''.join(response.xpath('//div[@class="news_nr3"]/p[position()<last()-1]|//p/span').extract())
		content_img_list = response.xpath("//div[@class='news_nr3']/p/span/img/@src").extract()
		img_list = []
		if len(content_img_list) >= 1:
			for index, value in enumerate(content_img_list):
				if '.gif' in value:
					content_img_list.pop(index)
		if len(content_img_list) >= 1:
			for index, value in enumerate(content_img_list):
				content_img_name = title + str(index) + '.jpg'
				res = send_file(content_img_name, value, self.config.get('send_url'), self.headers)
				if res['code'] == 1:
					image = res['data']['url']
					content = content.replace(value, image)
					img_list.append(image)
				else:
					self.logger.info(f'文章图片 {value} 上传失败，返回数据：{res}')
			content_imgs = ','.join(img_list)
		else:
			content_imgs = None
		source = response.xpath(self.content_source_xpath).re_first('来源：(.*?)\s')

		attachments = None
		item = ScrapyLhjQbzxItem()
		item['news_id'] = news_id
		item['category'] = '家电家居'
		item['sub_category'] = '家具产业'
		item['information_categories'] = '新闻资讯'
		item['content_url'] = response.url
		item['title'] = title  # 标题
		item['issue_time'] = issue_time  # 发布时间
		item['title_image'] = image  # 标题图片
		item['information_source'] = '家具在线'  # 网站名
		item['content'] = content  # 新闻的内容
		item['source'] = source  # 来源
		item['author'] = None
		item['attachments'] = attachments  # 附件
		item['area'] = None
		item['address'] = None
		item['tags'] = tags
		item['sign'] = '51'
		item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		item['cleaning_status'] = 0  #
		item['images'] = content_imgs  # content_img
		self.logger.info(item)
		yield item


if __name__ == '__main__':
	import scrapy.cmdline as cmd

	cmd.execute(['scrapy', 'crawl', 'grasp_jiagle'])
