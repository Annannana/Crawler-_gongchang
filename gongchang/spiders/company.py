# -*- coding: utf-8 -*-
import scrapy
from gongchang.items import GongchangItem
import re


class CompanySpider(scrapy.Spider):
    name = 'company'
    allowed_domains = ['mobile.gongchang.com']
    start_urls = ['https://mobile.gongchang.com/index.php?moduleid=4&catid=0&areaid=0']

    def parse(self, response):
        categories_links = response.xpath('//li[@class="two_directory" and not(contains(a,"全部"))]//a/@href').getall()
        categories = response.xpath('//li[@class="two_directory" and not(contains(a,"全部"))]//a/text()').getall()
        for category, link in zip(categories, categories_links):
            url = 'https://mobile.gongchang.com/'+link
            yield scrapy.Request(url=url, callback=self.parse_category,
                                 meta={'page': 1, 'category': category, 'base_url': url})

    def parse_category(self, response):
        page = response.meta.get("page")
        category = response.meta.get('category')
        base_url = response.meta.get('base_url')
        if page == 1:
            total_page = int(re.findall('.*?<b>1</b>/(.*?)</a>.*?', response.text)[0])
            for i in range(2, total_page+1):
                url = base_url +'&page='+str(i)
                yield scrapy.Request(url= url, callback=self.parse_category,
                                     meta={'page': i, 'category': category, 'base_url': base_url})

        for company in response.xpath("//div[@class='list-img']"):
            link = 'https://mobile.gongchang.com/' + company.xpath(".//a/@href").get('')
            item = GongchangItem()
            item['category'] = [category]
            item['name'] = company.xpath(".//strong/text()").get('')
            item['mainproduct'] = company.xpath(".//li[2]/span/text()").get('').split('：')[1].split(',')
            item['city'] = company.xpath(".//li[3]/span/text()").get('').split('\xa0\xa0')[0]
            # link = 'https://mobile.gongchang.com/index.php?moduleid=4&username=jichao'
            # link = 'https://mobile.gongchang.com/index.php?moduleid=4&username=kutekj'
            yield scrapy.Request(url=link, callback=self.parse_company,
                                 meta={'base_url': link, 'item': item})

    def parse_company(self, response):
        item = response.meta.get('item')
        base_url = response.meta.get('base_url')
        if response.xpath("//h1[@class='company']").get(''):#1
            item['phone'] = [response.xpath("//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][1]/div[@class='btm-item']/p[@class='dd']/text()").get('')]
            item['email'] = response.xpath("//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][2]/div[@class='btm-item']/p[@class='dd']/text()").get('')
            item['address'] = response.xpath("//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][3]/div[@class='btm-item']/p[@class='dd']/text()").get('')
            yield scrapy.Request(url=base_url+'&action=introduce',
                                 callback=self.parse_intro_1,
                                 meta={'base_url': base_url, 'item': item})
        else:#2
            item['linkman'] = response.xpath("//div[@class='content'][3]//text()").get('').split(':')[-1]
            phone = response.xpath("//div[@class='content'][3]/a[position()<3]/text()").getall()
            if len(phone)== 2 and phone[1] == phone[0]:
                phone = [phone[0]]
            item['phone'] = phone
            qq = response.xpath("//div[@class='content'][3]").re_first('.*?<br>Q  Q: (.*?)<br>.*?')
            if qq: item['qq'] =qq
            fax = response.xpath("//div[@class='content'][3]").re_first('.*?传 真: (.*?)<br>.*?')
            if fax: item['fax'] = fax
            item['address'] = response.xpath("//div[@class='content'][3]/a[position()=3]/text()").get('')
            yield scrapy.Request(url=base_url+'&action=introduce',
                                 callback=self.parse_intro_2,
                                 meta={'base_url': base_url, 'item': item})
    def parse_intro_1(self, response):
        item = response.meta.get('item')
        base_url = response.meta.get('base_url')
        item['intro'] = response.xpath("//div[@class='wangEditor-txt']/text()").get('')
        yield scrapy.Request(
            url=base_url + '&action=contact',
            callback=self.parse_contact_1,
            meta={'base_url': base_url, 'item': item})

    def parse_contact_1(self,response):
        item = response.meta.get('item')
        phone_1 = response.xpath("//div[@class='content']/p[5]/text()").get('').split('：')[-1]
        phone_2 = response.xpath("//div[@class='content']/p[8]/a/text()").get('').split('：')[-1]
        if phone_1 != '' and phone_1 not in item['phone']:
            item['phone'].append(phone_1)
        if phone_2 != '' and phone_2 not in item['phone']:
            item['phone'].append(phone_2)
        item['linkman'] = response.xpath("//div[@class='content']/p[7]/text()").get('').split('：')[-1]
        yield item

    def parse_intro_2(self, response):
        item = response.meta.get('item')
        base_url = response.meta.get('base_url')
        item['intro'] = response.xpath("string(//div[@class='content'])").get('')
        # response.xpath("//div[@class='content']").re_first('.*?</center>(.*?)</div>.*?', re.M)
        yield scrapy.Request(
            url=base_url + '&action=credit',
            callback=self.parse_credit_2,
            meta={'base_url': base_url, 'item': item})

    def parse_credit_2(self, response):
        item = response.meta.get('item')
        base_url = response.meta.get('base_url')

        info = response.xpath("//div[@class='content']/text()").getall()

        registeredcapital = [i.split('：')[-1] for i in info if '注册资本' in i]
        if registeredcapital: item['registeredcapital'] = registeredcapital[-1]
        businessstartedin = [i.split('：')[-1] for i in info if '注册年份' in i]
        if businessstartedin: item['businessstartedin'] = businessstartedin[-1]
        if response.xpath("//div[@class='content']/span[1]/text()").get('') == '通过营业执照认证':
            item['certificationenterprise'] = '企业资料通过营业执照认证'
        businessmodel = [i.split('：')[-1] for i in info if '经营模式' in i]
        if businessmodel: item['businessmodel'] = businessmodel[-1]
        companytype = [i.split('：')[-1] for i in info if '公司类型' in i]
        if companytype: item['companytype'] = companytype[-1]
        yield item
