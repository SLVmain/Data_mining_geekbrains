"""Источник: https://5ka.ru/special_offers/

Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы

результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные
сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл
и содержать товары исключительно соответсвующие данной категории.

пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}"""

import json
import time
import requests


class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt

class Parse5ka:
    params = {
        "records_per_page": 100,
        "page": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    }

    def __init__(self, start_url):
        self.start_url = start_url

    @staticmethod
    def __get_response(url, *args, **kwargs) -> requests.Response:
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

    def run(self):
        for products in self.parse(self.start_url):
            for product in products:
                self.save_to_json_file(product, product['id'])

    def parse(self, url):
        params = self.params
        while url:
            response = self.__get_response(url, params=params, headers=self.headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get("next")
            yield data.get('results')

    @staticmethod
    def save_to_json_file(data: dict, file_name):
        with open(f'products/{file_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)

class ParserCatalog(Parse5ka):

    def __init__(self, start_url, category_url):
        self.category_url = category_url
        super().__init__(start_url)

    def get_categories(self, url):
        response = requests.get(url, headers=self.headers)
        return response.json()

    def run(self):
        for category in self.get_categories(self.category_url):
            data = {
                "name": category['parent_group_name'],
                'code': category['parent_group_code'],
                "products": [],
            }

            self.params['categories'] = category['parent_group_code']

            for products in self.parse(self.start_url):
                data["products"].extend(products)

            self.save_to_json_file(
                data,
                category['parent_group_code']
            )


if __name__ == "__main__":
    #parser = Parse5ka('https://5ka.ru/api/v2/special_offers/')
    parser = ParserCatalog('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    parser.run()