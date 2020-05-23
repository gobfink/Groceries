#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

#TODO move this to a utility file?
def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script

class grocerySpider(scrapy.Spider):
    name = "grocery_spider"
    start_urls = ['https://grocery.walmart.com']
    #start_urls = ['https://www.target.com/c/grocery/-/N-5xt1a?Nao=0']

    def start_requests(self):
        lua = read_script("buttonClick.lua")
        print ("Lua script: " + lua)
        for url in self.start_urls:
            yield SplashRequest(url, self.scrape_urls, endpoint='execute', args={'lua_source': lua})

    def scrape_urls(self,response):
        #1. sort through data and extract urls
        #2. put urls together
        #3. Loop to each url, returning @parse
        base_url=self.start_urls[0]
        raw = response.body_as_unicode()
        remove=['"','{','}',' ']
        cleaned = raw
        for char in remove :
            cleaned = cleaned.replace(char,'')
        comma_split=cleaned.split(',')
        colon_split=[entry.split(':') for entry in comma_split]
        urls=[entry[-1] for entry in colon_split]
        print (urls)
        for url_end in urls:
            url = base_url + url_end
            print (url)
            yield SplashRequest(url, self.parse, endpoint='render.html',args={'wait':0.1})


    def parse(self, response):
        GROCERY_SELECTOR='[data-automation-id="productTile"]'
        SPONSORED_SELECTOR='[data-automation-id="sponsoredProductTile"]'
        GROCERIES_SELECTOR=GROCERY_SELECTOR+','+SPONSORED_SELECTOR

        #html = response.body_as_unicode()
        #print (html)
        #file = open("scraper.html","w")
        #n = file.write(html)
        #file.close()

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
        #inspect_response(response, self)
"""
        NEXT_PAGE_SELECTOR = '.next a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next:
            yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
            )
"""

