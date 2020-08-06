#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import re

from util import read_script, parse_float, lookup_category, get_next_url, get_url_metadata, store_url, clean_string, handle_none, finish_url

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
    location="8386 Sudley Road"
    """
    These are intialized in pipelines.py
    """
    conn = ""
    cursor = ""
    store_id=-1

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
        base_url = "https://www.walmart.com"
        self.raw = response.body_as_unicode()
        #print("raw: " + self.raw)
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
        #print("urls - ")
        #print(self.urls)

        section = "unset"
        subsection = "unset"

        self.section_dict = {}
        chars_to_remove=["\'","&"]
        for entry in self.colon_split:

            # each entry will have a subheading (normally at 0 unless it has a heading entry)
            section = clean_string(entry[0],chars_to_remove)
            url_end = clean_string(entry[-1],"\"")

            # if its a section header it will contain 3 entries
            #   and all subsequent entries will have the same heading
            if len(entry) > 2:
                section = clean_string(entry[0],chars_to_remove)
                subsection = clean_string(entry[1],chars_to_remove)

            url = base_url + url_end
            category=lookup_category("",section,subsection)
            store_url(self.conn,url,self.store_id,category,section,subsection)
            #self.section_dict[url] = (self.section, self.subsection)

            #print(section, subsection, url)

        next_url=get_next_url(self.cursor, 1)
        if next_url is None:
            print("No more urls to parse finishing")
        else:    
            yield SplashRequest(url,
                            self.parse,
                            endpoint='render.html',
                            args={
                                'wait': 10,
                                'section': section,
                                'subsection': subsection
                            })

    def parse(self, response):
        GROCERY_SELECTOR = '[data-automation-id="productTile"]'
        SPONSORED_SELECTOR = '[data-automation-id="sponsoredProductTile"]'
        GROCERIES_SELECTOR = GROCERY_SELECTOR + ',' + SPONSORED_SELECTOR
        NEXT_BUTTON = '[data-automation-id="nextButton"]'
        # Handle pagination
        url = response.url
        metadata=get_url_metadata(self.cursor,url)
        section=metadata[1]
        subsection=metadata[2]
        
        next_page=response.css(NEXT_BUTTON).get()
        if next_page is not None:
            #inspect_response(response,self)
            page_string="&page="
            page_str_len=len(page_string)
            i = url.find(page_string)
            #if yes, check url if it has a page part on it
            if i == -1:
            #if no, add page 2  to it
                next_url = url + page_string+"2"
            else:
            #if yes, extract page and add 1 
                page_number = i+page_str_len
                current_page = int(url[page_number:])
                next_page = current_page + 1
                next_url = url[:page_number] + str(next_page)
            #then add to self.urls
            store_url(self.conn,next_url, self.store_id, lookup_category("",section,subsection) ,section, subsection)


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
            #Check if the arrays returned from re.findall are empty
            if self.ounces:
                self.ounces = parse_float(self.ounces[0])
            else:
                self.ounces = 0
            if self.pounds:
                self.pounds = parse_float(self.pounds[0])
            else:
                self.pounds = 0
            if self.count:
                self.count = parse_float(self.count[0])
            else:
                self.count = 0



            if self.pounds != 0:
                self.ounces = 16*self.pounds
            elif self.count != 0:
                self.ounces *= self.count

            #            inspect_response(response,self)
            SALEPRICE_SELECTOR = '[data-automation-id="salePrice"] ::text'
            PRICE_SELECTOR = '[data-automation-id="price"] ::text'
            PRICE_PER_UNIT_SELECTOR = '[data-automation-id="price-per-unit"] ::text'

            name=grocery.css(NAME_SELECTOR).extract_first()
            name=clean_string(name,"\"")
            ounces=self.ounces
            pounds=self.pounds
            count=self.count
            price=str(handle_none(grocery.css(SALEPRICE_SELECTOR).extract_first())).replace('$','')
            ppu=convert_ppu(grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first())
            url=response.url

            yield {
                'name': name,
                'ounces': ounces,
                'pounds': pounds,
                'count': count,
                'price': price,
                'price-per-unit': ppu,
                'section': section,
                'subsection': subsection,
                'url': url,
            }

        finish_url(self.conn,self.store_id,url)
        next_url=get_next_url(self.cursor, 1)
        print(f"next_url - {next_url}")
        if next_url is None:
            print ("No more urls - finishing")
        else:
            yield SplashRequest(next_url,
                        self.parse,
                        endpoint='render.html',
                        args={
                            'wait': 10,
                            'section': section,
                            'subsection': subsection
                        })
