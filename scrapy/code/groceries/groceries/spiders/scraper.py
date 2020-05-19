#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest


class grocerySpider(scrapy.Spider):
    name = "grocery_spider"
    start_urls = ['https://grocery.walmart.com/']#, 'https://grocery.walmart.com/products?aisle=1255027787131_1255027789453']
    #start_urls = ['https://www.target.com/c/grocery/-/N-5xt1a?Nao=0']
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                    endpoint='render.html', args={'wait':5},
                    )

    def parse(self, response):
        GROCERY_SELECTOR='[data-automation-id="productTile"]'
        SPONSORED_SELECTOR='[data-automation-id="sponsoredProductTile"]'
        GROCERIES_SELECTOR=GROCERY_SELECTOR+','+SPONSORED_SELECTOR
        for grocery in response.css(GROCERIES_SELECTOR):

            NAME_SELECTOR   = '[data-automation-id="name"] ::attr(name)'
            SALEPRICE_SELECTOR  = '[data-automation-id="salePrice"] ::text'
            PRICE_SELECTOR  = '[data-automation-id="price"] ::text'
            PRICE_PER_UNIT_SELECTOR   = '[data-automation-id="price-per-unit"] ::text'
            #PIECES_SELECTOR = './/dl[dt/text() = "Pieces"]/dd/a/text()'
            #MINIFIGS_SELECTOR = './/dl[dt/text() = "Minifigs"]/dd[2]/a/text()'
            #IMAGE_SELECTOR = 'img ::attr(src)'
            yield {
                    'name': grocery.css(NAME_SELECTOR).extract_first(),
                    'sale-price': grocery.css(SALEPRICE_SELECTOR).extract_first(),
                    'price': grocery.css(PRICE_SELECTOR).extract_first(),
                    'price-per-unit': grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first(),
            }
        inspect_response(response, self)
"""
        NEXT_PAGE_SELECTOR = '.next a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next:
            yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
            )
"""

