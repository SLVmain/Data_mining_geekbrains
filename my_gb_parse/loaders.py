import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
#from .items import MyAutoyoulaItem
from .items import HHjobItem
from .items import HHcompanyItem

def get_company_url(item):
    base_url = "https://hh.ru/"
    return urljoin(base_url, item)


def join_to_string(values_list):
    res = ' '.join([x for x in values_list])
    return res


def clean_str(data:list):
    return ' '.join(data).replace('\xa0', '')

def get_url(data: list):
    add_url = str(''.join(data))
    return urljoin("https://hh.ru", add_url)


class HHjobLoader(ItemLoader):
    default_item_class = HHjobItem
    job_url_out = TakeFirst()
    job_title_out = TakeFirst()
    wage_out = clean_str
    job_description_in = ''.join
    job_description_out = TakeFirst()
    key_skills_out = TakeFirst()
    company_url_in = MapCompose(get_url)
    company_url_out = TakeFirst()

class HHcompanyLoader(ItemLoader):
    default_item_class = HHcompanyItem
    url_out = TakeFirst()
    company_title_in = clean_str
    company_title_out = TakeFirst()
    company_web_out = TakeFirst()
    activity_areas_out = TakeFirst()
    company_description_in = clean_str
    company_description_out = TakeFirst()




def get_author_id(item):
    re_str = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
    result = re.findall(re_str, item)
    return result

def get_author_url(item):
    base_url = "https://youla.ru/user/"
    return urljoin(base_url, item)

def clear_unicode(value):
    return value.replace("\u2009", "")

def in_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def get_specification(item):
    tag = Selector(text=item)
    name = tag.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').get()
    value = tag.xpath('//div[contains(@class, "AdvertSpecs_data")]//text()').get()
    return {name: value}

def specifications_output(values):
    result = {}
    for itm in values:
        result.update(itm)
    return result

"""class MyAutoyoulaLoader(ItemLoader):
    default_item_class = MyAutoyoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_unicode, in_float)
    price_out = TakeFirst()
    author_in = MapCompose(get_author_id, get_author_url)
    author_out = TakeFirst()
    specifications_in = MapCompose(get_specification)
    specifications_out = specifications_output"""


