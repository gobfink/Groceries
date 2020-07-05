#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re

from util import read_script, parse_float

def convert_ppu(incoming_ppu):
    if not incoming_ppu:
        return ""
    ppu = incoming_ppu
    charactersToRemove = ['$', '(',')']
    for remove in charactersToRemove:
        ppu = ppu.replace(remove,'')
    ppuSplit = ppu.split('/')
    cost = ppuSplit[0]
    if cost.find('cents') is not -1:
        cost = cost.replace('cents','')
        cost = cost.replace('.','')
        cost = "0."+ cost

    units = ppuSplit[1]
    if units == "FLUID OUNCE":
        units = "FLOZ"
    ppu = cost +" / "+units
    return ppu

class walmartSpider(scrapy.Spider):
    name = "walmart_spider"
    store_name = "walmart"
    start_urls = ['https://grocery.walmart.com']

    #start_urls = ['https://www.target.com/c/grocery/-/N-5xt1a?Nao=0']

    def start_requests(self):
        lua = read_script("buttonClick.lua")
        print("Lua script: " + lua)
        for url in self.start_urls:
            yield SplashRequest(url,
                                self.scrape_urls,
                                endpoint='execute',
                                args={'lua_source': lua})

    def scrape_urls(self, response):
        #1. sort through data and extract urls
        #2. put urls together
        #3. Loop to each url, returning @parse
        base_url = self.start_urls[0]
        self.raw = response.body_as_unicode()
        print("raw: " + self.raw)
        remove = ['{', '}', 'Link', ' ']
        self.cleaned = self.raw
        for char in remove:
            self.cleaned = self.cleaned.replace(char, '')
        self.comma_split = self.cleaned.split('","')
        #print ("cleaned - " + cleaned)
        #print ("comma_split - " )
        #print (*comma_split)
        self.colon_split = [entry.split('":"') for entry in self.comma_split]
        #inspect_response(response, self)
        self.colon_split[0].remove('"sections')
        #print ("colon_split - ")
        #print (*colon_split)
        self.urls = [entry[-1] for entry in self.colon_split]
        print("urls - ")
        print(self.urls)

        self.section = "unset"
        self.subsection = "unset"

        self.section_dict = {}
        for entry in self.colon_split:

            # each entry will have a subheading (normally at 0 unless it has a heading entry)
            self.subsection = entry[0]
            url_end = entry[-1]

            # if its a section header it will contain 3 entries
            #   and all subsequent entries will have the same heading
            if len(entry) > 2:
                self.section = entry[0]
                self.subsection = entry[1]

            url = base_url + url_end
            self.section_dict[url] = (self.section, self.subsection)

            print(self.section, self.subsection, url)
            yield SplashRequest(url,
                                self.parse,
                                endpoint='render.html',
                                args={
                                    'wait': 10,
                                    'section': self.section,
                                    'subsection': self.subsection
                                })

    def parse(self, response):
        GROCERY_SELECTOR = '[data-automation-id="productTile"]'
        SPONSORED_SELECTOR = '[data-automation-id="sponsoredProductTile"]'
        GROCERIES_SELECTOR = GROCERY_SELECTOR + ',' + SPONSORED_SELECTOR
        url = response.url
        section = self.section_dict[url][0]
        subsection = self.section_dict[url][1]
        for grocery in response.css(GROCERIES_SELECTOR):
            NAME_SELECTOR = '[data-automation-id="name"] ::attr(name)'
            self.name = grocery.css(NAME_SELECTOR).extract_first()
            #parse the ounces off of the name
            decimal_regex = "([\d]+[.]?[\d]*|[.\d]+)"
            self.ounces = re.findall(decimal_regex + "\s*o(?:z|unces?)",
                                     self.name, re.IGNORECASE)
            self.pounds = re.findall(decimal_regex + "\s*(?:pound|lb)s?",
                                     self.name, re.IGNORECASE)
            self.count = re.findall("([\d]+)\s*(?:c(?:t|ount)|p(?:k|ack))",
                                    self.name, re.IGNORECASE)

            self.ounces = parse_float(self.ounces)
            self.pounds = parse_float(self.pounds)
            self.count = parse_float(self.count)

            if self.pounds != 0:
                self.ounces = 16*self.pounds
            elif self.count != 0:
                self.ounces *= self.count

            #            inspect_response(response,self)
            SALEPRICE_SELECTOR = '[data-automation-id="salePrice"] ::text'
            PRICE_SELECTOR = '[data-automation-id="price"] ::text'
            PRICE_PER_UNIT_SELECTOR = '[data-automation-id="price-per-unit"] ::text'

            yield {
                'name':
                grocery.css(NAME_SELECTOR).extract_first(),
                'ounces':
                self.ounces,
                'pounds':
                self.pounds,
                'count':
                self.count,
                'price':
                grocery.css(SALEPRICE_SELECTOR).extract_first().replace('$',''),
                'price-per-unit':
                convert_ppu(grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first()),
                'section':
                section,
                'subsection':
                subsection,
                'url':
                response.url,
            }
