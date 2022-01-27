from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from Leroy.spiders.LeroySpider import LeroyspiderSpider
from Leroy import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyspiderSpider)

    process.start()