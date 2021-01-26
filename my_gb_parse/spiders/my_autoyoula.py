"""Источник https://auto.youla.ru/
Обойти все марки авто и зайти на странички объявлений
Собрать след стуркутру и сохранить в БД Монго
Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить номер телефона"""

import scrapy
import base64


class MyAutoyoulaSpider(scrapy.Spider):
    name = 'my_autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    css_query = {
        "brands": "div.TransportMainFilters_brandsList__2tIkv div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "div.SerpSnippet_titleWrapper__38bZM a.blackLink",
    }

    @staticmethod
    def gen_tasks(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib.get("href"), callback=callback)

    def parse(self, response):
        yield from self.gen_tasks(
            response, response.css(self.css_query["brands"]), self.brand_parse
        )

    def brand_parse(self, response):
        yield from self.gen_tasks(
            response, response.css(self.css_query["pagination"]), self.brand_parse
        )
        yield from self.gen_tasks(response, response.css(self.css_query["ads"]), self.ads_parse)

    def ads_parse(self, response):
        pattern = r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar'
        user_id = response.css('script::text').re_first(pattern)

        pattern1 = r'phone%22%2C%22(\w+)'
        phone = response.css('script::text').re_first(pattern1)
        phone = base64.b64decode(base64.b64decode(phone + '==')).decode("utf-8")

        yield  {
            "title": response.css("div.AdvertCard_advertTitle__1S1Ak::text").get(),
            "price": response.css("div.AdvertCard_price__3dDCr::text").get(),
            "description": response.css("div.AdvertCard_descriptionInner__KnuRi::text").get(),
            "images": response.css("img.PhotoGallery_photoImage__2mHGn::attr(src)").getall(),
            "features_dict" : dict(zip(response.css("div.AdvertSpecs_label__2JHnS::text").getall(),
                               response.css("div.AdvertSpecs_data__xK2Qx *::text").getall())
                                   ),
            "user_url" : (f'https://youla.ru/user/{user_id}'),
            "phone" : phone
        }

        #print(data)

#https://youla.ru/user/5a165fdcc15ae372b56c5294

#api/get-youla-profile



