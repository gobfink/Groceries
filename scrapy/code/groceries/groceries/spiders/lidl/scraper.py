#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re

#TODO move this to a utility file?
def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script


def parse_float(input_list):
    if input_list:
        f = float(input_list[0])
    else:
        f = 0
    return f


class lidlScraper(scrapy.Spider):
    name = "lidl_spider"
    store_name = "lidl"
    start_urls = ['https://www.lidl.com/products']
    base_url = "https://www.lidl.com"
    expand_and_scroll_lua = read_script("prepareForScraping.lua")

    def start_requests(self):
        print ("lua script - " + self.expand_and_scroll_lua)
        for url in self.start_urls:
            yield SplashRequest(url,
                                self.isTop,
                                args={'wait': 0.5})

    def isTop(self, response):
        # This callback determines if the selected menu is 
        # at the top of the list, if it is then it adds the urls 
        # to the list and keeps going
        # if its not, then it calls the lua to prepare the page 
        # for scraping, and then scrapes it  
        menu = response.css(".category-filter__link")
        print ("processing response.url - " + response.url)
        print ("menu: ")
        print (menu.getall())
        print ("len(menu): " + str(len(menu)))
        if (len(menu) > 0  and menu[0].css('[aria-current="page"]')):
            print("top page active - for "+ menu[0].get())
            urls=menu.css('::attr(href)').getall()
            # Remove the the first(this) page from list to parse
            urls.pop()
            for url_suffix in urls:
                url = self.base_url + url_suffix
                print ("pulling from url - " + url)
                yield SplashRequest(url,
                                self.isTop,
                                endpoint='execute',
                                args={'lua_source': self.expand_and_scroll_lua})

            # The top page is active
            # therefore we need to scrape the links, and continue searching
            # we then need to loop through each other page.
            # call isTop, and scrape it is not
        else:
            #we are on a subpage, so now we can start scraping
            print("subpage - scraping " + response.url)
            #inspect_response(response, self)
            #    
        #active
        #print(menu)

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
                'sale-price':
                grocery.css(SALEPRICE_SELECTOR).extract_first(),
                'price':
                grocery.css(PRICE_SELECTOR).extract_first(),
                'price-per-unit':
                grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first(),
                'section':
                section,
                'subsection':
                subsection,
            }
