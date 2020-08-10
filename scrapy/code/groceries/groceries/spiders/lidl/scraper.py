#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re

from util import read_script, convert_cents, store_url, get_next_url, get_url_metadata, lookup_category, finish_url

def convert_ppu(incoming_ppu):
    if not incoming_ppu:
        return ""
    ppu = incoming_ppu
    charactersToRemove = ['$', ' ']
    for remove in charactersToRemove:
        ppu = ppu.replace(remove,'')
    if ppu.find('per') is not -1:
        ppuSplit = ppu.split('per')
    elif ppu.find('each') is not -1:
        # Split off the each, and add it on manually
        ppuSplit = ppu.split('each')
        print ("ppu - " + ppu + ", ppuSplit - " + str(ppuSplit))
        # Add 'each' as the units to be set appropriately
        ppuSplit[1] = 'ea'

    cost = ppuSplit[0]
        # if theirs a / seperating multiple values
    if cost.find('/'):
        temp_cost = ""
        costs = cost.split('/')
        for c in costs:
            c = convert_cents(c)
            # If its the first value
            if temp_cost == "":
                temp_cost = c
            else:
                temp_cost = temp_cost + ", " + c
            cost = temp_cost
        else:
            cost = convert_cents(cost)

    units = ppuSplit[1]
    units = units.replace('.','')
    units = units.upper()
    ppu = cost +" / "+units
    return ppu

class lidlScraper(scrapy.Spider):
    name = "lidl_spider"
    store_name = "lidl"
    start_urls = ['https://www.lidl.com/products']
    base_url = "https://www.lidl.com"
    expand_and_scroll_lua = read_script("prepareForScraping.lua")
    section_dict = {}
    urls = []
    processedUrls = []
    location = "default"

    def start_requests(self):
        print ("lua script - " + self.expand_and_scroll_lua)
        for url in self.start_urls:
            yield SplashRequest(url,
                                self.parse,
                                args={'wait': 0.5})

    def parse(self, response):
        # This callback determines if the selected menu is 
        # at the top of the list, if it is then it adds the urls 
        # to the list and keeps going
        # if its not, then it calls the lua to prepare the page 
        # for scraping, and then scrapes it  
        url = response.url
        
        menu = response.css(".category-filter__link")
        #submenu = response.css("")
        #print ("self.urls - " +str(self.urls))
        print ("processing response.url - " + response.url)

        #print ("menu: ")
        #print (menu.getall())
        #print ("len(menu): " + str(len(menu)))
        #print ("menu[0] : " + menu.get())
        #print("name - " + menu[0].css('.category-filter__text ::text').get())
        #inspect_response(response,self)

        if (len(menu) > 0  and menu[0].css('[aria-current="page"]')):
            print (f"inside menu page for url - {url}")
            # The top page is active
            #print ("menu[0] : [aria-current=page] " + menu[0].css('[aria-current="page"]').get())
            # therefore we need to scrape the links, and continue searching
            # we then need to loop through each other page.
            # call parse, and scrape it is not
            menu_url=menu[0].css('::attr(href)').get()

            menu_name=menu[0].css('.category-filter__text ::text').get()
            for item in menu:
                heading = item.css('.category-filter__text ::text').get()
                scraped_url = item.css('::attr(href)').get()
                scraped_url = self.base_url+scraped_url
                section=menu_name
                subsection=heading
                category=lookup_category("",section,subsection)
                store_url(self.conn,scraped_url,self.store_id,category,section,subsection)

                #self.section_dict[url]=(menu_name, heading)
                #if self.urls.count(url) == 0:
                #    self.urls.append(url)


            #urls=menu.css('::attr(href)').getall()
            # Remove the the first(this) page from list to parse
            #urls.pop()
            #self.urls.extend(urls)
            #print("urls to scrape - " + str(self.urls))
            #print("local urls - " + str(urls))

            """
            while len(self.urls) != 0:
                url = self.urls.pop()
                self.processedUrls.append(url)
                #url = self.base_url + url_suffix
                #print ("urls - " + str(self.urls))
                #print ("pulling from url - " + url)
                #print ("urls lengths - " + str(len(self.urls)))
                yield SplashRequest(url,
                                self.parse,
                                endpoint='execute',
                                args={'lua_source': self.expand_and_scroll_lua})
            """

        elif (len(menu) == 0):
            inspect_response(response, self)

        else:
            #we are on a subpage, so now we can start scraping
            #    
        
            GROCERY_SELECTOR = '.grid-item'
            NAME_SELECTOR = '.small-type.detail-card-description ::text'
            PRICE_SELECTOR = '.price ::text'
            PRICE_PER_UNIT_SELECTOR = '.sub-headline.detail-card-subtext ::text'
            
            
            metadata = get_url_metadata(self.cursor,url)
            section = metadata[0]
            subsection = metadata[1]
            print("subpage - scraping " + url + ", from section - "+section)
            for grocery in response.css(GROCERY_SELECTOR):
                self.name = grocery.css(NAME_SELECTOR).extract_first()
                self.price = grocery.css(PRICE_SELECTOR).extract_first()
                if self.price is not None:
                    self.price = self.price.replace('*','').replace('$','')
                self.ppu = grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first()
                if self.ppu is not None:
                    self.ppu = convert_ppu(self.ppu) 
                #inspect_response(response, self)
                #parse the ounces off of the name
                yield {
                    'name':
                    self.name,
                    'price':
                    self.price,
                    'price-per-unit':
                    self.ppu,
                    'section':
                    section,
                    'subsection':
                    subsection,
                    'url':
                    response.url
                }
        finish_url(self.conn,self.store_id,url)
        print("finishing url - " + url)
        next_url = get_next_url(self.cursor, 1)
        print("got next_url - " +next_url)
        if next_url is not None:
            yield SplashRequest(next_url,
                                self.parse,
                                endpoint='execute',
                                dont_filter=True,
                                args={'lua_source': self.expand_and_scroll_lua})
