from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from my_gb_parse.spiders.my_autoyoula import MyAutoyoulaSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("my_gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(MyAutoyoulaSpider)
    crawler_process.start()
