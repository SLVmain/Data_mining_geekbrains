# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline

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

"""class GbImagePipeline(ImagesPipeline): #рабочий вариант для загрузки картинок, убрала для второй домашки по инста 
    def get_media_requests(self, item, info):

        img_url = item.get('images', [])
        yield Request(img_url)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        return item"""

"""class GbImagePipeline(ImagesPipeline): #загрузка картинок с работы на уроке
    def get_media_requests(self, item, info):
        for img_url in item.get('images', []):
            yield Request(img_url)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        return item"""

# вариант с урока
"""class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for img_url in item.get('images', []):
        if isinstance(item, InstaPost):
            pass
        to_download = []
        to_download.extend(item.get("images", []))
        if item["data"].get("display_url"):
            to_download.append(item["data"]["display_url"])
        for img_url in to_download:
            yield Request(img_url)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        item["images"] = [itm[1] for itm in results]
        return item"""

"""class MyGbParsePipeline: #мой вариант домашки урок 04
    def __init__(self):
        self.conn = pymongo.MongoClient('localhost', 27017)
        db = self.conn["autoyoula"]
        self.collection = db['auto_ads']

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item"""
        
"""class GbparsImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        images = item.get('img',item['data'].get('profile_pic_url',item['data'].get('display_url',[])))

        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]
        except KeyError:
            pass
        return item"""