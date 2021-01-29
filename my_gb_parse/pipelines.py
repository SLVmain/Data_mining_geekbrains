# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

"""class MyGbParsePipeline:
    def process_item(self, item, spider):
        return item"""

class MyGbParsePipeline:
    def process_item(self, item, spider):
        return item

class SaveToMongo:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client['my_gb_parse']

    def process_item(self, item, spider):

        self.db[spider.name].insert_one(item)
        return item


"""class MyGbParsePipeline: #мой вариант домашки урок 04
    def __init__(self):
        self.conn = pymongo.MongoClient('localhost', 27017)
        db = self.conn["autoyoula"]
        self.collection = db['auto_ads']

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item"""