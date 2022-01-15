
import re
from lxml import html
import requests
from pymongo import MongoClient
from pprint import pprint
import datetime
from pymongo.errors import DuplicateKeyError


headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}

url = "https://news.mail.ru/"

response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)

items = dom.xpath(
    '//table//span[contains(@class, "_title")] | //div[contains(@data-module, "TrackBlocks")]//a[contains(@class, "list__text")]')


client = MongoClient("localhost", 27017)
db = client["news_database"]
news = db.news
news.create_index('name', unique=True)
for el in items:
    article = {}
    name = el.xpath('./text()')[0].replace(u'\xa0', ' ')
    url = el.xpath('../../@href | ./@href')[0]
    r = requests.get(url, headers=headers)
    article_page = html.fromstring(r.text)
    source = article_page.xpath(
        '//span[@class="note"]//span[contains(@class, "link__text")]/text()')[0]
    date = article_page.xpath(
        '//span[contains(@class, "js-ago")]/@datetime')[0]
    article['name'] = name
    article['url'] = url
    article['source'] = source
    article['date'] = date
    try:
        news.insert_one(article)
    except DuplicateKeyError:
        print("Ошибка, новость уже в базе")
