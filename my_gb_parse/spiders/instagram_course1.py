import json
import scrapy
from collections import deque


class Instagram_course1Spider(scrapy.Spider):
    name = 'instagram'
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    api_url = "/graphql/query/"
    followed_by_list = []
    i_follow_list = []

    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32',
        'i_follow': '3dec7e2c57367ef3da3d987d89f9dbc8',
        'followed_by': '5aefa9893005572d237da5068082d8d5',
    }


    def __init__(self, login, password, *args, **kwargs):
        self.__login = login
        self.__password = password
        super().__init__(*args, **kwargs)



    def parse(self, response):

        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.__login,
                    'enc_password': self.__password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                q = deque()
                visited = set() #хотела сделать массивом, но решила сделать так для увеличения скорости поиска
                prev = dict()
                start = self.users[0]
                finish = self.users[1]
                q.append(start)
                visited.add(start)
                prev[start] = ''
                done = False

                if (len(self.followed_by_list) == counts['followed_by_total']) and (len(self.i_follow_list) == counts['i_follow_total']):



                    while len(q) > 0 and not done:
                        user = q.popleft()
                        yield response.follow(f"/{user}/", callback=self.insta_page_user_parse)

                        for next_user in self.followed_by_list:
                            if (not (next_user in visited)) and next_user in self.i_follow_list:
                                if next_user == finish:
                                    prev[next_user] = user
                                    done = True
                                    break
                                q.append(next_user)
                                visited.add(next_user)
                                prev[next_user] = user

                    if finish not in prev.keys():
                        print('нет такой цепи рукопожатий')
                        return

                path = []
                t = finish
                while t != '':
                    path.append(t)
                    t = prev[t]
                path.reverse()
                print(f'длина цепи рукопожатий: {len(path)}\nцепь: {path}')


    def insta_page_user_parse(self, response):
        user_data = self.js_data_extract(response)["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        variables = {
                "id": user_data["id"],
                "first": 100,
            }

        followed_by_total = user_data['edge_followed_by']['count']
        i_follow_total = user_data['edge_follow']['count']

        self.followed_by_list = []

        url_followed_by = f'{self.api_url}?query_hash={self.query_hash["followed_by"]}&variables={json.dumps(variables)}'
        yield response.follow(url_followed_by, callback=self.get_followed_res, cb_kwargs={"user_data": user_data},
                              counts = {"followed_by_total": followed_by_total})


        self.i_follow_list = []

        url_i_follow = f'{self.api_url}?query_hash={self.query_hash["i_follow"]}&variables={json.dumps(variables)}'
        yield response.follow(url_i_follow, callback=self.get_i_follow_res, cb_kwargs={"user_data": user_data},
                              counts = {"i_follow_total": i_follow_total})


    def get_followed_res (self, response, user_data):

        data1 = response.json()
        followed_by_data = data1["data"]["user"]["edge_followed_by"]["edges"]

        if data1["data"]["user"]["edge_followed_by"]["page_info"]["has_next_page"]:
            variables = {
                "id": user_data["id"],
                "first": 100,
                "after": data1["data"]["user"]["edge_followed_by"]["page_info"]["end_cursor"],
            }
            url_pag = f'{self.api_url}?query_hash={self.query_hash["followed_by"]}&variables={json.dumps(variables)}'

            for user in followed_by_data:
                self.followed_by_list.append(user["node"]["username"])
            yield response.follow(url_pag, callback=self.get_followed_res, cb_kwargs={"user_data": user_data})


    def get_i_follow_res (self, response, user_data):

        data2 = response.json()
        i_follow_data = data2["data"]["user"]["edge_follow"]["edges"]

        if data2["data"]["user"]["edge_follow"]["page_info"]["has_next_page"]:
            variables = {
                "id": user_data["id"],
                "first": 100,
                "after": data2["data"]["user"]["edge_follow"]["page_info"]["end_cursor"],
            }
            url_pag = f'{self.api_url}?query_hash={self.query_hash["i_follow"]}&variables={json.dumps(variables)}'

            for user in i_follow_data:
                self.i_follow_list.append(user["node"]["username"])
            yield response.follow(url_pag, callback=self.get_i_follow_res, cb_kwargs={"user_data": user_data})



    @staticmethod
    def js_data_extract(response) -> dict:
        script = response.xpath("/html/body/script[contains(text(), 'window._sharedData = ')]/text()").get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
