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

class lidlScraper(scrapy.Spider):
    name = "lidl_spider"
    store_name = "lidl"
    start_urls = ['https://www.lidl.com/products']
    base_url = "https://www.lidl.com"
    expand_and_scroll_lua = read_script("prepareForScraping.lua")
    section_dict = {}
    urls = []
    processedUrls = []

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
                self.ppu = grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first()
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
