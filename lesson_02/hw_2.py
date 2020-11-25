import requests
from urllib.parse import urljoin
import bs4
import pymongo as pm


class MagnitParser:

    def __init__(self, start_url):
        self.start_url = start_url
        mongo_client = pm.MongoClient()
        self.db = mongo_client['parse_geekbrains']

    def _get(self, url: str) -> bs4.BeautifulSoup:
        # todo обработока статусов и повторные запросы
        response = requests.get(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self._get(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup: bs4.BeautifulSoup) -> dict:
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.findChildren('a'):
            try:
                integer_new = product.find('div',attrs={'class': 'label__price label__price_new'}).find('span', attrs={'class': 'label__price-integer'}).text
                decimal_new = product.find('div',attrs={'class': 'label__price label__price_new'}).find('span', attrs={'class': 'label__price-decimal'}).text
                price_new = float(integer_new) + float(decimal_new) / 100

                integer_old = product.find('div',attrs={'class': 'label__price label__price_old'}).find('span', attrs={'class': 'label__price-integer'}).text
                decimal_old = product.find('div',attrs={'class': 'label__price label__price_old'}).find('span', attrs={'class': 'label__price-decimal'}).text
                price_old = float(integer_old) + float(decimal_old) / 100
                pr_data = {
                    'url': urljoin(self.start_url, product.attrs.get('href')),
                    'promo_name': product.find('div', attrs={'class': 'card-sale__header'}).find('p').text,
                    'product_name': product.find('div', attrs={'class': 'card-sale__title'}).text,
                    'image_url': urljoin(self.start_url, product.find('img').attrs.get('data-src')),
                    'new_price': price_new,
                    'old_price': price_old,
                    #'date_from': "DATETIME",
                    #'date_to': "DATETIME",

                }
                yield pr_data
            except AttributeError:
                continue


    def save(self, data: dict):
        collection = self.db['magnit']
        collection.insert_one(data)


if __name__ == '__main__':
    parser = MagnitParser('https://magnit.ru/promo/?geo=moskva')
    parser.run()
