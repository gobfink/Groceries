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
import re

from util import (read_script, store_url, get_next_url,
                  get_url_metadata, lookup_category, finish_url, get_next_pagination,
                  trim_url, convert_to_ounces, convert_units, clean_string)

class safewayScraper(scrapy.Spider):
    name = "safeway_grocery_spider"
    store_name = "safeway"
    start_urls = ["https://www.safeway.com/shop/aisles.1431.html"]
    base_url = "https://www.safeway.com"

    section_dict = {}
    urls = []
    processedUrls = []
    location = "12821 Braemar Village Plaza"
    zipcode = "20136"
    page_str="?sort=&page="


    # @description the start function for the scraper. Kicks off the scraping
    def start_requests(self):

        location_request = create_parse_request(self.start_urls[0],
                                                self.check_location,
                                                EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
        yield location_request

    # @description changes the locaion of the webpage.
    # @TODO if it doesn't find the location it will just hang
    # @param zipcode - string : zipcode of the location to change to
    # @param location - string : address of the location of the store to change to
    def change_location(self, zipcode, location):
        print(f"changing location to {self.location}")
        change_button = self.driver.find_element_by_css_selector('#openFulfillmentModalButton')
        change_button.click()
        zip_input = self.driver.find_element_by_css_selector('[aria-labelledby="zipcode"]')
        zip_input.send_keys(zipcode)
        zip_input.send_keys(Keys.RETURN)
        time.sleep(2)
        stores = self.driver.find_elements_by_css_selector('.card-store')

        for store in stores:
            caption = store.find_element_by_css_selector('.caption').text
            print (f"store - {store}, {caption}")
            if location in caption:
                print (f"found {location} in {caption}")
                button = store.find_element_by_css_selector('[role="button"]')
                button.click()
                time.sleep(5)
                break
    # @decription checks the location on the website and compares it with that on the scraper
    #             if its the same it continues, if not it will call change_location to change it
    # @called is a callback via a yield function
    # @calls parse
    # @param response - html response of the webpage
    def check_location(self, response):
        self.driver=response.request.meta['driver']
        current_location = self.driver.find_element_by_css_selector('.reserve-nav__current-instore-text').text
        print(f"current_location = {current_location} and it should be {self.location}")
        if current_location != self.location:
            print ("changing location")
            self.change_location(self.zipcode,self.location)
        else:
            print(f"current location is already {current_location} == {self.location}")

        #Now that we've checked the location now lets pass it to the parsing section
        if response.url.find(self.page_str) != -1:
            print(f'{response.url} has page string')
            scrape_request = create_unfiltered_parse_request(response.url,
                                                             self.parse,
                                                             EC.element_to_be_clickable((By.CSS_SELECTOR,'product-item-v2')))
                                                             #EC.element_to_be_clickable((By.CSS_SELECTOR,'.add-product [role="button"]')))
        else:
            print()
            scrape_request = create_unfiltered_parse_request(response.url,
                                                             self.parse,
                                                             EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))

        yield scrape_request

    # @description first scrapes the urls, then goes through and parses the groceries from the webpage
    # @param response - html response of the webpage
    def parse(self, response):
        page_1_str=self.page_str+"1"
        meta_url = response.meta.get('url')
        this_url = response.url #trim_url(response.url,page_1_str)
        trimmed_url = trim_url(response.url,page_1_str)
        print (f"inside parse for meta_url: {meta_url}, response.url: {response.url}")

        # Only scrape pages that have the page_str in the url.
        if this_url.find(self.page_str) == -1 :
            print(f"Skipping {this_url} because it couldn't find {self.page_str}")
        elif meta_url != response.url:
            print(f"meta_url: {meta_url} != response.url: {response.url}, and so we are finishing stale {meta_url}")
            this_url = meta_url
        else:
            print (f"scraping for {this_url}")
            items = response.css('product-item-v2')
            print(f"length of items - {len(items)}")
            ## FIXME For some reason the middleware is returning an empty response for all of the urls that reach here.
            #inspect_response(response,self)
            metadata=get_url_metadata(self.cursor,trimmed_url)
            if len(metadata) != 3:
                print(f"Couldn't detect metadata: {metadata}, for trimmed_url: {trimmed_url}, defaulting to empty")
                section=""
                subsection=""
            else:
                section=metadata[1]
                subsection=metadata[2]

            for item in items:
                name = item.css('.product-title ::text').get()
                price_string = item.css('.product-price').get()
                price = re.findall("\$([0-9]+\.[0-9]+)", price_string)[0]
                ppu = item.css('.product-price-qty ::text').get()
                unit = self.collect_units(name)

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
        print("finishing url - " + this_url + ", store_id: ", self.store_id)
        next_url = get_next_url(self.cursor, 1,self.store_id,filter="page=")
        if next_url is None:
            print ("Next url is none therefore we must be finished ! ")
            return
        else:
            #next_request = create_unfiltered_parse_request(next_url,
            #                                    self.check_location,
            #                                    EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
            next_request = create_unfiltered_parse_request(next_url,
                                                self.parse,
                                                EC.element_to_be_clickable((By.CSS_SELECTOR,'product-item-v2')))
        print(f"got next_url - {next_url}")
        yield next_request

    # @description collects and returns the ounces from the grocery
    # @param string - string to collect the ounces from
    # @returns 0 if no ounces could be detected - else returns the ounces
    def collect_ounces(self,string):
        split = string.split(' - ')
        ounces = 0

        if len(split) == 1:
            print (f"No -'s found in {string} - not updating ounces")
        elif len(split) == 2:
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
        return ounces

    # @description collects the units from the grocery
    # @param string - string to collect the units from
    # @returns - empty string if it can't find units. Else returns the units from the string
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
