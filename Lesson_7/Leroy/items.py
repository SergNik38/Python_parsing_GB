# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(value):
    try:
        value = int(value.replace(' ', ''))
    except Exception:
        pass
    return value


class LeroyItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(clear_price))
    url = scrapy.Field(output_processor=TakeFirst())
