# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client['books']

    def process_item(self, item, spider):
        if not item['author']:
            item['author'] = None
        name = item['name'].split(':')[1:]
        name = ':'.join(name).strip()
        if name:
            item['name'] = name
        if item['old_price']:
            item['old_price'] = int(item['old_price'].strip().replace(u'\xa0', '').split(' ')[0])
        item['price'] = int(item['price'].strip().split(' ')[0])
        item['rating'] = float(item['rating'].strip().replace(',', '.'))
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
