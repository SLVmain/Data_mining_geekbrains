"""Источник https://geekbrains.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:

url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
список тегов
реализовать SQL структуру хранения данных c следующими таблицами

Post
Comment
Writer
Tag
Организовать реляционные связи между таблицами

При сборе данных учесть, что полученый из данных автор уже может быть в БД и значит необходимо это заблаговременно проверить.
Не забываем закрывать сессию по завершению работы с ней"""

import os
import time
import requests
import bs4
from dotenv import load_dotenv
from urllib.parse import urljoin
import database

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt

class GbParse:
    def __init__(self, start_url, db):
        self.db = db
        self.start_url = start_url
        self.done_url = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_url.add(self.start_url)

    """"@staticmethod
    def _get_response(*args, **kwargs):
        # TODO обработки ошибок
        return requests.get(*args, **kwargs)"""

    @staticmethod
    def _get_response(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

    def _get_soup(self, *args, **kwargs):
        response = self._get_response(*args, **kwargs)
        return bs4.BeautifulSoup(response.text, "lxml")

    def parse_task(self, url, callback):
        def wrap():
            soup = self._get_soup(url)
            return callback(url, soup)

        return wrap

    def run(self):
        for task in self.tasks:

            result = task()
            if result:
                self.save(result)

    def pag_parse(self, url, soup):
        for a_tag in soup.find("ul", attrs={"class": "gb__pagination"}).find_all("a"):

            pag_url = urljoin(url, a_tag.get("href"))
            if pag_url not in self.done_url:
                task = self.parse_task(pag_url, self.pag_parse)
                self.tasks.append(task)
            self.done_url.add(pag_url)
        for a_post in soup.find("div", attrs={"class": "post-items-wrapper"}).find_all(
            "a", attrs={"class": "post-item__title"}
        ):

            post_url = urljoin(url, a_post.get("href"))
            if post_url not in self.done_url:
                task = self.parse_task(post_url, self.post_parse)
                self.tasks.append(task)
            self.done_url.add(post_url)

    def post_parse(self, url, soup):

        title = soup.find("h1", attrs={"class": "blogpost-title"}).text
        author_name_tag = soup.find("div", attrs={"itemprop": "author"})
        img_url = soup.find('img').get('src')
        post_datetime = soup.find("time", attrs={"class": "text-md text-muted m-r-md"}).get("datetime")

        author = {
            "url": urljoin(url, author_name_tag.parent.get("href")),
            "name": author_name_tag.text,
        }
        tags = [
            {"name": tag.text, "url": urljoin(url, tag.get("href"))}
            for tag in soup.find("article").find_all("a", attrs={"class": "small"})
        ]

        post_comments_id = soup.findAll('div', {'class': 'm-t-xl'})[0].find('comments')[
            'commentable-id']
        comments_ = requests.get(
            f"https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id={post_comments_id}&order=desc")
        data: dict = comments_.json()
        comments = []
        for i in range(0, len(data)):
            user = data[i]['comment']['user']['id']
            body = data[i]['comment']['body']
            comments.append({'author_id': user, 'body': body})

        return {
            "post_data": {
                "url": url,
                "title": title,
                "img_url": img_url,
                "post_date": post_datetime,
            },
            "author": author,
            "tags": tags,
            "comments": comments
        }

    def save(self, data: dict):
        print(data)
        self.db.create_post(data)


if __name__ == "__main__":
    load_dotenv('.env')
    parser = GbParse("https://geekbrains.ru/posts", database.Database(os.getenv("SQLDB_URL")))
    parser.run()