from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from my_gb_parse.spiders.my_autoyoula import MyAutoyoulaSpider
from my_gb_parse.spiders.hh import HHSpider
import os
from dotenv import load_dotenv
from my_gb_parse.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    tags = ['python', 'programming']
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule("my_gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    #crawler_process.crawl(MyAutoyoulaSpider)
    #crawler_process.crawl(HHSpider)
    crawler_process.crawl(InstagramSpider, login=os.getenv('USERNAME'), password=os.getenv('ENC_PASSWORD'), tags=tags)
    crawler_process.start()



