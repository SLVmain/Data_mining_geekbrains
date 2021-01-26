from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from my_gb_parse.spiders.my_autoyoula import MyAutoyoulaSpider


"""def run(self):
    for product in self.parse(self.start_url):
        self.save(product)

def save(self):
    for ads_item in self.ads_parse():
        collection = self.database["autoyoula"]
        collection.insert_one(ads_item)"""

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("my_gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(MyAutoyoulaSpider)
    crawler_process.start()
