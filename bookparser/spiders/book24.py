import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem
from time import sleep


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    page = 1
    start_urls = [f'https://book24.ru/best-price/']

    def parse(self, response: HtmlResponse):
        if response.xpath('//a[contains(@class, "product-card__image-link")]/@href').get():
            self.page += 1
            next_page = f'{self.start_urls[0]}page-{self.page}/'
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains(@class, "product-card__image-link")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[@itemprop="name"]/text()').get()
        author = response.xpath(
            '//span[contains(text(), "Автор")]/../..//a[contains(@class, "product-characteristic-link")]/text()').getall()
        old_price = response.xpath('//span[contains(@class, "price-old")]/text()').get()
        price = response.xpath('//span[@class="app-price product-sidebar-price__price"]/text()').get()
        url = response.url
        rating = response.xpath('//span[@class="rating-widget__main-text"]/text()').get()
        yield BookparserItem(name=name, author=author, old_price=old_price, price=price, url=url, rating=rating)
