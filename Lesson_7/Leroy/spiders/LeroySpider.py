import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from Leroy.items import LeroyItem


class LeroyspiderSpider(scrapy.Spider):
    name = 'LeroySpider'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/elektroinstrumenty/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="product-image"]')
        for link in links:
            yield response.follow(link, callback=self.parse_products)

    def parse_products(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]//source'
                                   '[contains(@media, "only screen and (min-width: 1024px)")]/@srcset')
        loader.add_xpath('price', '//span[@slot="price"]//text()')
        loader.add_value('url', response.url)
        yield loader.load_item()