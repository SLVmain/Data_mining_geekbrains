# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyGbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HHjobItem(scrapy.Item):
    _id = scrapy.Field()
    job_url = scrapy.Field()
    job_title = scrapy.Field()
    wage = scrapy.Field()
    job_description = scrapy.Field()
    key_skills = scrapy.Field() #в виде списка
    company_url = scrapy.Field()


class HHcompanyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    company_title = scrapy.Field()
    company_web = scrapy.Field() #если есть
    activity_areas = scrapy.Field() #в виде списка
    company_description = scrapy.Field()
    company_vacancies = scrapy.Field()




"""class MyAutoyoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    specifications = scrapy.Field()
    price = scrapy.Field()"""

