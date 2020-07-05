#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re
from util import read_script, convert_cents
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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

class wegmansScraper(scrapy.Spider):
    name = "wegmans_spider"
    store_name = "wegmans"  
    start_urls = ['https://shop.wegmans.com/shop/categories']
    #Need to double check this
    base_url = "https://shop.wegmans.com/shop/categories"
    #expand_and_scroll_lua = read_script("prepareForScraping.lua")
    section_dict = {}
    urls = []
    processedUrls = []

    def __init__(self):
        #self.start_url = "https://shop.wegmans.com/shop/categories"
        #self.driver = webdriver.Firefox()
        #self.driver.implicitly_wait(20)

    def start_requests(self):
        yield SeleniumRequest(
            url=self.start_urls[0],
            callback=self.parse,
            wait_time=10,
            wait_until=EC.visibility_of((By.ID, 'catalog-category-24'))
        )
        #print ("lua script - " + self.expand_and_scroll_lua)
        #yield SplashRequest(self.start_url, self.parse, endpoint='render.html', args={'wait': 10})

    def parse(self, response):
        #self.driver.get(response.url)
        #beef=self.driver.find_element_by_id("catalog-category-24")
        h=response.text
        print("Looking for Beef - " + str(h.find("Beef")))
        # This callback determines if the selected menu is 
        # at the top of the list, if it is then it adds the urls 
        # to the list and keeps going
        # if its not, then it calls the lua to prepare the page 
        # for scraping, and then scrapes it  
        inspect_response(response,self)
        return

        menu = response.css(".category-filter__link")
        #submenu = response.css("")
        #print ("self.urls - " +str(self.urls))
        print ("processing response.url - " + response.url)

        #print ("menu: ")
        #print (menu.getall())
        #print ("len(menu): " + str(len(menu)))
        #print ("menu[0] : " + menu.get())
        #print("name - " + menu[0].css('.category-filter__text ::text').get())

        if (len(menu) > 0  and menu[0].css('[aria-current="page"]')):
            # The top page is active
            #print ("menu[0] : [aria-current=page] " + menu[0].css('[aria-current="page"]').get())
            # therefore we need to scrape the links, and continue searching
            # we then need to loop through each other page.
            # call parse, and scrape it is not
            menu_url=menu[0].css('::attr(href)').get()

            menu_name=menu[0].css('.category-filter__text ::text').get()
            for item in menu:
                heading = item.css('.category-filter__text ::text').get()
                url = item.css('::attr(href)').get()
                url = self.base_url+url
                self.section_dict[url]=(menu_name, heading)
                if self.urls.count(url) == 0:
                    self.urls.append(url)


            #urls=menu.css('::attr(href)').getall()
            # Remove the the first(this) page from list to parse
            #urls.pop()
            #self.urls.extend(urls)
            #print("urls to scrape - " + str(self.urls))
            #print("local urls - " + str(urls))


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


        elif (len(menu) == 0):
            inspect_response(response, self)

        else:
            #we are on a subpage, so now we can start scraping
            #    
        
            GROCERY_SELECTOR = '.grid-item'
            NAME_SELECTOR = '.small-type.detail-card-description ::text'
            PRICE_SELECTOR = '.price ::text'
            PRICE_PER_UNIT_SELECTOR = '.sub-headline.detail-card-subtext ::text'
            
            url = response.url
            sections = self.section_dict[url]
            section = sections[0]
            subsection = sections[1]
            print("subpage - scraping " + response.url + ", from section - "+section)
            for grocery in response.css(GROCERY_SELECTOR):
                self.name = grocery.css(NAME_SELECTOR).extract_first()
                self.price = grocery.css(PRICE_SELECTOR).extract_first()
                self.price = self.price.replace('*','').replace('$','')
                self.ppu = convert_ppu(grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first())
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
