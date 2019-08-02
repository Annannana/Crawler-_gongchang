# -*- coding: utf-8 -*-
import scrapy
from gongchang.items import GongchangItem
import re


class CompanySpider(scrapy.Spider):
    name = 'company'
    allowed_domains = ['mobile.gongchang.com']
    start_urls = ['https://mobile.gongchang.com/index.php?moduleid=4&catid=0&areaid=0']
    cities_numbers = ['1', '2', '3', '4', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47',
                      '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63',
                      '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
                      '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95',
                      '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109',
                      '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '123',
                      '124', '125', '126', '127', '128', '129', '130', '131', '132', '133', '134', '135', '136', '137',
                      '138', '139', '140', '141', '142', '143', '144', '145', '146', '147', '148', '149', '150', '151',
                      '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165',
                      '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177', '178', '179',
                      '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191', '192', '193',
                      '194', '195', '196', '197', '198', '199', '200', '201', '202', '203', '204', '205', '206', '207',
                      '208', '209', '210', '211', '212', '213', '214', '215', '216', '217', '218', '219', '220', '221',
                      '222', '223', '224', '225', '226', '227', '228', '229', '230', '231', '232', '233', '234', '235',
                      '236', '237', '238', '239', '240', '241', '242', '243', '244', '245', '246', '247', '248', '249',
                      '250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263',
                      '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '277',
                      '278', '279', '280', '281', '282', '283', '284', '285', '286', '287', '288', '289', '290', '291',
                      '292', '293', '294', '295', '296', '297', '298', '299', '300', '301', '302', '303', '304', '305',
                      '306', '307', '308', '309', '310', '311', '312', '313', '314', '315', '316', '317', '318', '319',
                      '320', '321', '322', '323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '333',
                      '334', '335', '336', '337', '338', '339', '340', '341', '342', '343', '344', '345', '346', '347',
                      '348', '349', '350', '351', '352', '353', '354', '355', '356', '357', '358', '359', '360', '361',
                      '362', '363', '364', '365', '366', '367', '368', '369', '370', '371', '372', '373', '374', '375',
                      '376', '377', '378', '379', '380', '381', '382', '383', '384', '385', '386', '387', '388', '389',
                      '390', '391', '32', '33', '34']

    def parse(self, response):
        # get all categories and their links
        categ = response.xpath("//li[@class='directory']/text()").getall()
        categories_links = []
        categories = []
        index = 1
        for each in response.xpath("//div[@id='second_list']/ul"):
            self.logger.info('index:'+str(index))
            if (index > 1 and index < 5) or index == 7:
                categories_links.extend(
                    each.xpath('.//li[@class="two_directory" and not(contains(a,"全部"))]//a/@href').getall())
                categories.extend(
                    each.xpath('.//li[@class="two_directory" and not(contains(a,"全部"))]//a/text()').getall())
            elif index == 5 or index == 6:
                categories_links.extend(each.xpath('.//li[@class="two_directory"]//a/@href').getall())
                categories.append(categ[index-1])

        index += 1

        # for testing
        categories_links = ['index.php?moduleid=4&catid=20019&areaid=0']
        categories = ['代理']
        for category, link in zip(categories, categories_links):
            url = 'https://mobile.gongchang.com/' + link
            yield scrapy.Request(url=url, callback=self.parse_category,
                                 meta={'page': 1, 'category': category, 'base_url': url})

    def parse_category(self, response):
        page = response.meta.get("page")
        category = response.meta.get('category')
        base_url = response.meta.get('base_url')
        check = False  # if the category need add city

        if page == 1:
            total_page = re.findall('.*?<b>1</b>/(.*?)</a>.*?', response.text)
            if total_page:
                total_page = int(total_page[0])

            if total_page == 50 and 'areaid=0' in base_url:
                check = True
                self.logger.info('TOTAL PAGE LARGER THAN 50, PLEASE DOUBLE CHECK IT.')
                for numbers in self.cities_numbers:
                    url = base_url.replace('areaid=0', 'areaid=' + numbers)
                    yield scrapy.Request(url=url, callback=self.parse_category,
                                         meta={'page': 1, 'category': category, 'base_url': url})
            if not check and total_page:
                for i in range(2, total_page + 1):
                    url = base_url + '&page=' + str(i)
                    yield scrapy.Request(url=url, callback=self.parse_category,
                                         meta={'page': i, 'category': category, 'base_url': base_url})
        if not check:
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
        if response.xpath("//h1[@class='company']").get(''):  # 1
            item['phone'] = [response.xpath(
                "//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][1]/div[@class='btm-item']/p[@class='dd']/text()").get(
                '')]
            item['email'] = response.xpath(
                "//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][2]/div[@class='btm-item']/p[@class='dd']/text()").get(
                '')
            item['address'] = response.xpath(
                "//div[@class='pure-u-1-1 pure-u-md-1-3 pure-box mf-item'][3]/div[@class='btm-item']/p[@class='dd']/text()").get(
                '')
            yield scrapy.Request(url=base_url + '&action=introduce',
                                 callback=self.parse_intro_1,
                                 meta={'base_url': base_url, 'item': item})
        else:  # 2
            item['linkman'] = response.xpath("//div[@class='content'][3]//text()").get('').split(':')[-1]
            phone = response.xpath("//div[@class='content'][3]/a[position()<3]/text()").getall()
            if len(phone) == 2 and phone[1] == phone[0]:
                phone = [phone[0]]
            item['phone'] = phone
            qq = response.xpath("//div[@class='content'][3]").re_first('.*?<br>Q  Q: (.*?)<br>.*?')
            if qq: item['qq'] = qq
            fax = response.xpath("//div[@class='content'][3]").re_first('.*?传 真: (.*?)<br>.*?')
            if fax: item['fax'] = fax
            item['address'] = response.xpath("//div[@class='content'][3]/a[position()=3]/text()").get('')
            yield scrapy.Request(url=base_url + '&action=introduce',
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

    def parse_contact_1(self, response):
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
