import scrapy
import json
import re
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'raccoonva1era'
    inst_passw = "#PWD_INSTAGRAM_BROWSER:10:1643803232:AahQACyUyOz+D9RfTKbEnk8SRpMochXvw04caCbvgqtDOrI3uKmJb2lCBZhhqdAf3" \
                 "RxtMTY4TcfSomPBcBz7Q32Jvcq9NDjTfgf3AUNJ2ps4ykLxK++Sd+YmskrGjphM2oBttsB8ov79qzfVC/+Kcvl7fA=="
    user_for_parse = ['transsibgrupp_baikal', 'veretennikova1661']

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_passw},
                                 headers={'X-CSRFToken': csrf_token})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.user_for_parse:
                yield response.follow(f'/{user}',
                                      callback=self.subs_parse,
                                      cb_kwargs={'username': user})

    def subs_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page'

        yield response.follow(url,
                              callback=self.subscribers_parse_next,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

        url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12'

        yield response.follow(url,
                              callback=self.subscription_parse_next,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

    def subscribers_parse_next(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        pass
        max_id = j_data.get('next_max_id')
        if max_id:
            url = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?' \
                  f'count=12&search_surface=follow_list_page&max_id={max_id}'

            yield response.follow(url,
                                  callback=self.subscribers_parse_next,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  cb_kwargs={'username': username,
                                             'user_id': user_id})

        subs = j_data.get('users')
        for sub in subs:
            item = InstaparserItem(
                user_id=sub.get('pk'),
                username=sub.get('username'),
                full_name=sub.get('full_name'),
                profile_pic=sub.get('profile_pic_url'),
                parsed_user_id=user_id,
                status='subscriber'
            )
            yield item


    def subscription_parse_next(self, response: HtmlResponse, username, user_id):
        j_data_following = response.json()
        max_id_following = j_data_following.get('next_max_id')
        if max_id_following:
            url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?' \
                  f'count=12&max_id={max_id_following}'

            yield response.follow(url,
                                  callback=self.subscription_parse_next,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  cb_kwargs={'username': username,
                                             'user_id': user_id})

        subscriptions = j_data_following.get('users')
        for follow in subscriptions:
            item = InstaparserItem(
                user_id=follow.get('pk'),
                username=follow.get('username'),
                full_name=follow.get('full_name'),
                profile_pic=follow.get('profile_pic_url'),
                parsed_user_id=user_id,
                status='subscription'
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
