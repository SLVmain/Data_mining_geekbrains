import json
import scrapy
import datetime
from ..items import IGTagItem, IGPostItem, IGUserItem, IGFollowedByItem, IGIFolloweItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    tag_path = '/explore/tags/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    api_url = "/graphql/query/"

    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32',
        'i_follow': '3dec7e2c57367ef3da3d987d89f9dbc8',
        'followed_by': '5aefa9893005572d237da5068082d8d5',
    }

    def __init__(self, login, password, tags: list, *args, **kwargs):
        self.__login = login
        self.__password = password
        self.tags = tags
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
                #for tag in self.tags:
                    #tag_url = f'{self.tag_path}{tag}'
                    #yield response.follow(tag_url, callback=self.tag_parse)
                for user in self.users:
                    yield response.follow(f"/{user}/", callback=self.insta_page_user_parse)
                        #для домашки 2 другой вариант окончания parse, ссылка формируется подстановкой имени пользователя

    def insta_page_user_parse(self, response):
        user_data = self.js_data_extract(response)["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        # yield user_data
        yield IGUserItem(
            date_parse = datetime.datetime.utcnow(),
            data = user_data
        )
    #variables{"id": "277609170", "include_reel": true, "fetch_mutual": true, "first": 24}
        variables = {
                "id": user_data["id"],
                "first": 100,
            }
        url_followed_by = f'{self.api_url}?query_hash={self.query_hash["followed_by"]}&variables={json.dumps(variables)}'
        yield response.follow(url_followed_by, callback=self.get_followed_res, cb_kwargs={"user_data": user_data})

        url_i_follow = f'{self.api_url}?query_hash={self.query_hash["i_follow"]}&variables={json.dumps(variables)}'
        yield response.follow(url_i_follow, callback=self.get_i_follow_res, cb_kwargs={"user_data": user_data})

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
            yield response.follow(url_pag, callback=self.get_followed_res, cb_kwargs={"user_data": user_data})


        for user in followed_by_data:
            yield IGFollowedByItem(
                user_id=user_data["id"],
                user_name=user_data["username"],
                followed_by_id=user["node"]["id"],
                followed_by_name=user["node"]["username"],
            )

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
            yield response.follow(url_pag, callback=self.get_i_follow_res, cb_kwargs={"user_data": user_data})

        for user in i_follow_data:
            yield IGIFolloweItem(
                user_id=user_data["id"],
                user_name=user_data["username"],
                i_follow_id=user["node"]["id"],
                i_follow_name=user["node"]["username"],
            )







    def tag_parse(self, response):
        graphql = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        yield IGTagItem(
            date_parse = datetime.datetime.utcnow(),
            tag_id = graphql['id'],
            tag_name = graphql['name'],
            images = graphql['profile_pic_url']
        )

        yield from self.instagram_posts_page_parse(response)



    def instagram_posts_page_parse(self, response):
        try:
            data = self.js_data_extract(response)
            graphql = data['entry_data']['TagPage'][0]['graphql']

        except AttributeError:
            data = json.loads(response.text)
            graphql = data['data']

        hashtag_name = graphql['hashtag']['name']
        edges = graphql['hashtag']['edge_hashtag_to_media']['edges']
        url_start_graphql = 'https://www.instagram.com/graphql/query/?'

        for itm in edges:
            yield IGPostItem(
                date_parse=datetime.datetime.utcnow(),
                node = itm['node'],
                images = itm['node']['display_url'],
            )

        _page_info = graphql['hashtag']['edge_hashtag_to_media']['page_info']

        if _page_info['has_next_page']:

            _tag_name = f'"tag_name"%3A"{hashtag_name}"'
            _first = f'"first"%3A100'
            _end_cursor = _page_info['end_cursor']
            _after = f'"after"%3A"{_end_cursor}"'
            final_url = f'{url_start_graphql}query_hash=9b498c08113f1e09617a1703c22b2f32&variables=%7B{_tag_name},{_first},{_after}%7D'

            yield response.follow(final_url, callback=self.instagram_posts_page_parse, )



    @staticmethod
    def js_data_extract(response) -> dict:
        script = response.xpath("/html/body/script[contains(text(), 'window._sharedData = ')]/text()").get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
