# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GongchangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    mainproduct = scrapy.Field()
    city = scrapy.Field()
    intro = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    address = scrapy.Field()
    qq = scrapy.Field()
    fax = scrapy.Field()
    linkman = scrapy.Field()
    registeredcapital = scrapy.Field()
    businessstartedin = scrapy.Field()
    certificationenterprise = scrapy.Field()
    businessmodel = scrapy.Field()
    companytype = scrapy.Field()

    linkmanexpand = scrapy.Field()
    memberlevel = scrapy.Field()
    emploees = scrapy.Field()
    mainindustry = scrapy.Field()
