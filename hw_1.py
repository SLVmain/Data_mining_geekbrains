import json
import time
import requests

cat_url = 'https://5ka.ru/api/v2/categories/'
main_url = 'https://5ka.ru/api/v2/special_offers/'

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0'}
def parse5ka (url, params):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if params:
            params = {}
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result

if __name__ == '__main__':
    # Все категории
    response = requests.get(cat_url, headers=headers)
    catalogs = response.json()

    for i in range(len(catalogs)):
        data = parse5ka(main_url, {'categories': catalogs[i].get('parent_group_code')})
        f_name = catalogs[i].get('parent_group_code')
        with open(f'products/{f_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)
