"""Источник https://magnit.ru/promo/?geo=moskva
Необходимо собрать структуры товаров по акции и сохранить их в MongoDB

пример структуры и типы обязательно хранить поля даты как объекты datetime
{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}"""
import requests
from urllib.parse import urljoin
import bs4
import pymongo
import time
import datetime
import os
from dotenv import load_dotenv

months_dict = {'янв' : 1, 'фев' : 2, 'мар' : 3, 'апр' : 4, 'май' : 5, 'июн' : 6,
               'июл' : 7, 'авг' : 8, 'сен' : 9, 'окт' : 10, 'ноя' : 11, 'дек' : 12}

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt

class MagnitParser:
    def __init__(self, start_url, data_base):
        self.start_url = start_url
        self.database = data_base["gb_parse_12_01_2021"]

    @staticmethod
    def __get_response(url, *args, **kwargs):
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue



    @staticmethod
    def __get_soup(response):
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        for product in self.parse(self.start_url):
            self.save(product)

    def parse(self, url):
        soup = self.__get_soup(self.__get_response(url))
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.findChildren('a'):
            try:
                integer_new = product.find('div',attrs={'class': 'label__price label__price_new'}).find('span', attrs={'class': 'label__price-integer'}).text
                decimal_new = product.find('div',attrs={'class': 'label__price label__price_new'}).find('span', attrs={'class': 'label__price-decimal'}).text
                price_new = float(integer_new) + float(decimal_new) / 100

                integer_old = product.find('div',attrs={'class': 'label__price label__price_old'}).find('span', attrs={'class': 'label__price-integer'}).text
                decimal_old = product.find('div',attrs={'class': 'label__price label__price_old'}).find('span', attrs={'class': 'label__price-decimal'}).text
                price_old = float(integer_old) + float(decimal_old) / 100

                raw_dates = product.find('div', attrs={'class': 'card-sale__date'}).text
                raw_dates = raw_dates.split('\n')


                pr_data = {
                    'url': urljoin(self.start_url, product.attrs.get('href')),
                    'promo_name': product.find('div', attrs={'class': 'card-sale__header'}).find('p').text,
                    'product_name': product.find('div', attrs={'class': 'card-sale__title'}).text,
                    'image_url': urljoin(self.start_url, product.find('img').attrs.get('data-src')),
                    'old_price': price_old,
                    'new_price': price_new,
                    'date_from': string_to_date(raw_dates[1]),
                    'date_to': string_to_date(raw_dates[2])
                }

                yield pr_data
            except AttributeError:
                continue


    def save(self, data):
        collection = self.database["magnit_product"]
        collection.insert_one(data)


def string_to_date(raw_date):
    raw_date = raw_date.split()
    return datetime.datetime(2021, months_dict[raw_date[2][:3]], int(raw_date[1]))

if __name__ == "__main__":
    load_dotenv('.env')
    data_base = pymongo.MongoClient(os.getenv("DATA_BASE_URL"))
    parser = MagnitParser("https://magnit.ru/promo/?geo=moskva", data_base)
    parser.run()
