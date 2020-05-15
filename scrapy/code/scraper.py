#! /usr/local/bin/python3

import scrapy

class grocerySpider(scrapy.Spider):
    name = "grocery_spider"
    start_urls = ['https://grocery.walmart.com/']
    
    def parse(self, response):
        GROCERY_SELECTOR='div[data-automation-id]="productionTileDetails"'
        GROCERY_SELECTOR='.productionTile'
        for grocery in response.css(GROCERY_SELECTOR):
            PRICE_SELECTOR  = ''
            NAME_SELECTOR   = 'title ::text'
            NAME_SELECTOR   = 'span[data-automation-id]="name"'
            PIECES_SELECTOR = './/dl[dt/text() = "Pieces"]/dd/a/text()'
            MINIFIGS_SELECTOR = './/dl[dt/text() = "Minifigs"]/dd[2]/a/text()'
            IMAGE_SELECTOR = 'img ::attr(src)'
            yield {
                    'name': grocery.css(NAME_SELECTOR).extract_first(),
            }
"""
        NEXT_PAGE_SELECTOR = '.next a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next:
            yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
            )
"""

