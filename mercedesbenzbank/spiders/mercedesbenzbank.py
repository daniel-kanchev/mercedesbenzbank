import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from mercedesbenzbank.items import Article


class mercedesbenzbankSpider(scrapy.Spider):
    name = 'mercedesbenzbank'
    start_urls = ['https://www.mercedes-benz-bank.de/content/mbbank/de/newsroom/blog/2021.html']

    def parse(self, response):
        years = response.xpath('//ul[@class="MB_tab-list"]/li/a/@href').getall()
        yield from response.follow_all(years, self.parse_years, dont_filter=True)

    def parse_years(self, response):
        links = response.xpath('//span[@class="MB_text"][text()="Mehr erfahren! "]/ancestor::a/@href').getall() + \
                response.xpath('//span[@class="MB_text"][text()="Mehr erfahren"]/ancestor::a/@href').getall()

        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="MB_footnote-target"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
