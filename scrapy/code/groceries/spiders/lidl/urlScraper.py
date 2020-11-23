#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re

from util import read_script, store_url, get_next_url, lookup_category, finish_url


class lidlUrlScraper(scrapy.Spider):
    name = "lidl_url_spider"
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


        elif (len(menu) == 0):
            inspect_response(response, self)

        finish_url(self.conn,self.store_id,url,True)
        print("finishing url - " + url)
        next_url = get_next_url(self.cursor, 1,self.store_id, True)

        if next_url is not None:
            print("got next_url - " +next_url)
            yield SplashRequest(next_url,
                                self.parse,
                                endpoint='execute',
                                dont_filter=True,
                                args={'lua_source': self.expand_and_scroll_lua})
        else:
            print ("Next url is none therefore we must be finished ! ")
