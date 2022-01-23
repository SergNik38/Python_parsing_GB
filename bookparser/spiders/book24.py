import scrapy


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/best-price/']

    def parse(self, response, **kwargs):

        print(response.url)
