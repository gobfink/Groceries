#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumHelpers import create_parse_request, create_unfiltered_parse_request
import time
#TODO change to selenium so that we can update the location!!!
import re

from util import read_script, convert_cents, store_url, get_next_url, get_url_metadata, lookup_category, finish_url, get_next_pagination, trim_url, convert_to_ounces, convert_units, clean_string

def convert_ppu(incoming_ppu):
    if not incoming_ppu:
        return ""
    ppu = incoming_ppu
    charactersToRemove = ['$', ' ']
    for remove in charactersToRemove:
        ppu = ppu.replace(remove,'')
    if ppu.find('per') != -1:
        ppuSplit = ppu.split('per')
    elif ppu.find('each') != -1:
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

class safewayScraper(scrapy.Spider):
    name = "safeway_spider"
    store_name = "safeway"
    start_urls = ["https://www.safeway.com/shop/aisles.1431.html"]
    base_url = "https://www.safeway.com"

    #expand_and_scroll_lua = read_script("prepareForScraping.lua")
    section_dict = {}
    urls = []
    processedUrls = []
    location = "12821 Braemar Village Plaza"
    zipcode = "20136"
    page_str="?sort=&page="

    def start_requests(self):
        #print ("lua script - " + self.expand_and_scroll_lua)
        #wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton'))
        location_request = create_parse_request(self.start_urls[0],self.check_location,EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
        yield location_request

    def change_location(self):
        print(f"changing location to {self.location}")
        change_button = self.driver.find_element_by_css_selector('#openFulfillmentModalButton')
        change_button.click()
        zip_input = self.driver.find_element_by_css_selector('[aria-labelledby="zipcode"]')
        zip_input.send_keys(self.zipcode)
        zip_input.send_keys(Keys.RETURN)
        time.sleep(2)
        stores = self.driver.find_elements_by_css_selector('.card-store')

        for store in stores:
            caption = store.find_element_by_css_selector('.caption').text
            print (f"store - {store}, {caption}")
            if self.location in caption:
                print (f"found {self.location} in {caption}")
                button = store.find_element_by_css_selector('[role="button"]')
                button.click()
                time.sleep(5)
                break

        #yield self.location_request


    def check_location(self, response):
        self.driver=response.request.meta['driver']
        current_location = self.driver.find_element_by_css_selector('.reserve-nav__current-instore-text').text
        print(f"current_location = {current_location}")
        if current_location != self.location:
            print ("changing location")
            self.change_location()
        else:
            print(f"current location is already {current_location} == {self.location}")

        scrape_request = create_unfiltered_parse_request(self.start_urls[0],self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
        yield scrape_request

    def scrape_urls(self,response):
        #view_alls = response.css('.text-uppercase.view-all-subcats ::attr(href)').getall()
        mainGroups = response.css('.col-12.col-sm-12.col-md-4.col-lg-4.col-xl-3')
        #TODO can probably infer some categories from location
        for mainGroup in mainGroups:
            view_all = mainGroup.css('.text-uppercase.view-all-subcats ::attr(href)').get()
            view_all_url = self.base_url + view_all
            section = mainGroup.css('.product-title.text-uppercase ::text').get()
            section = section.strip()
            category = lookup_category("",section,"")
            #print (f"view_all_url - {view_all_url}, section - {section}, category - {category}")
            store_url(self.conn,view_all_url,self.store_id, category,section,"")

        siblingAisles = response.css('.siblingAisle')
        for siblingAisle in siblingAisles:
            href = siblingAisle.css('::attr(href)').get()
            siblingAisleUrl = self.base_url + href
            section = response.css('[aria-current="location"] ::text').get()
            section = section.strip()
            subsection = siblingAisle.css('::text').get()
            subsection = subsection.strip()
            category = lookup_category("",section,subsection)
            store_url(self.conn,siblingAisleUrl,self.store_id,category,section,subsection)
#
        #check if it has a load-more button and then increment page number on it
        if response.css('.primary-btn.btn.btn-default.btn-secondary.bloom-load-button').get() is not None:
            path = response.css('[aria-current]:not(.menu-nav__sub-item) ::text').getall()
            #print(f"path - {path} for url - {response.url}")
            section = path[1]
            section = section.strip()
            subsection = path[-2]
            subsection = subsection.strip()
            category = lookup_category("",section,subsection)
            next_page_url=get_next_pagination(self.page_str,response.url)
            print (f'load-more-button. storing - {next_page_url}, section - {section}, subsection - {subsection}, category - {category}')
            store_url(self.conn,next_page_url,self.store_id,category,section,subsection)

    def parse(self, response):
        page_1_str=self.page_str+"1"
        this_url = trim_url(response.url,page_1_str)
        print (f"inside parse for {this_url}")
        self.scrape_urls(response)

        # Only scrape pages that have the page_str in the url.
        if this_url.find(self.page_str) != -1:
            print (f"scraping for {this_url}")
            items = response.css('product-item-v2')
            print(f"length of items - {len(items)}")
            metadata=get_url_metadata(self.cursor,this_url)
            section=metadata[1]
            subsection=metadata[2]
            for item in items:
                name = item.css('.product-title ::text').get()
                price_strings = item.css('.product-price ::text').getall()
                price = clean_string(price_strings[-1],['$'])
                ppu = item.css('.product-price-qty ::text').get()
                unit = self.collect_units(name)
                #inspect_response(response,self)

                if unit == "OZ" or unit == "LB":
                    ounces = self.collect_ounces(name)
                else:
                    ounces = 0
                print (f"yielding - {name}, {price}, {ppu}, {ounces}, {unit}")
                yield{
                  "name": name,
                  "price": price,
                  "ounces": ounces,
                  "unit": unit,
                  "price-per-unit": ppu,
                  "url": this_url,
                  "section": section,
                  "subsection": subsection
                }

        #Basically the website redirects us to the url and page_1_str, which isn't added to our database
        # So we trim that off so we can get the url in our database
        finish_url(self.conn,self.store_id,this_url)
        print("finishing url - " + this_url)
        next_url = get_next_url(self.cursor, 1)
        if next_url is None:
            print ("Next url is none therefore we must be finished ! ")
            return
        elif next_url.find(self.page_str) != -1:
            print('next-url has page string')
            next_request = create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR,'.add-product [role="button"]')))     
        else:
            next_request = create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
            #next_request = create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR,'.product-title')))     
        print("got next_url - " +next_url)
        yield next_request
    
    def collect_ounces(self,string):
        split = string.split(' - ')
        ounces = 0

        if len(split) == 1:
            print (f"No -'s found in {string} - not updating ounces")
        elif len(split) == 2:
            #FIXME Sometimes they don't uses spaces between quantity and weight
            weight = split[1]
            ounces = convert_to_ounces(weight)
        elif len(split) == 3:
            quantity = split[1]
            weight = convert_to_ounces(split[2])
            quantity = clean_string(quantity,["Count"])
            if quantity.isdigit():
                quantity=int(quantity)
            else:
                quantity=1
            ounces = weight * quantity
        else:
            print(f"Collect_ounces too many '-'s in string {string}")
            ounces = 0
        return ounces
    def collect_units(self,string):
        #Assuming the form `Name - <amount> <units>`
        ## i.e. Signature Care Hand Soap Clear Moisturizing - 7.5 Fl. Oz. 
        #Also has the form `Name - <quantity>-<amount> <units>`
        ## i.e. SPF 50 - 2-9.1 Oz 
        #print (f"Working on string - {string}")
        split_off_name = string.split(' - ')
        if len(split_off_name) < 2 :
            print(f"unable to collect units from {string}")
            return ""
        unit_section = split_off_name[-1]
        #print(f"unit-section - {unit_section}")
        quantity=1
        if unit_section.find('-') != -1:
            # If theirs still a hyphen then we have a quantity to parse off first
            quantity_split = unit_section.split('-')
            if quantity_split[0].isdigit():
                quantity = int(quantity_split[0])
            unit_section = quantity_split[-1]

        #Now we should be in the form X.X Units
        decimal_regex = "([\d]+[.]?[\d]*|[.\d]+)"
        complete_regex = decimal_regex+"(.*)"
        decimal_broken = re.findall(complete_regex,unit_section)
        #print(f"collect_units, quantity - {quantity}, decimal - {decimal_broken}")
        if len(decimal_broken) == 0:
            # if its in the Name - EA form 
            # Just Use the EA as the units
            decimal_broken = unit_section
        elif type(decimal_broken[0]) is tuple:
            decimal_broken=list(decimal_broken[0])
        unit = convert_units(decimal_broken[-1])

        return unit
