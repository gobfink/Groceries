#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import NoSuchElementException


from seleniumHelpers import create_parse_request, create_unfiltered_parse_request
import time
import re

from util import (read_script, store_url, get_next_url,
                  get_url_metadata, lookup_category, finish_url, get_next_pagination,
                  trim_url, convert_to_ounces, convert_units, clean_string, 
                  is_section_in_store_id, is_subsection_in_store_id)



class harristeeterGroceryScraper(scrapy.Spider):
    name = "harris-teeter-grocery_spider"
    store_name = "harris-teeter"
    start_urls = ["https://www.harristeeter.com/shop/store/313"]
    base_url = start_urls[0]

    location = "10438 Bristow Center Dr"
    zipcode = "20136"
    page_str="?sort=&page="
    delay=10

    def start_requests(self):
        print("inside start_requests")
        ADD_TO_CART_SELECTOR='#product-main > div.forlistview-right > span > a.btn.btn-primary'
        next_url = get_next_url(self.cursor, 1)
        while next_url is not None:
            current_url = next_url
            scrape_url_request = create_parse_request(current_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR,ADD_TO_CART_SELECTOR)))
            yield scrape_url_request
            next_url = get_next_url(self.cursor,1)

    # @param response - html response of the webpage
    def parse(self, response):
        url = response.url
        print (f"inside parse for {url}")
        PRODUCTS_CSS='#product-main'
        metadata=get_url_metadata(self.cursor,url)
        section=metadata[1]
        subsection=metadata[2]
        products = response.css(PRODUCTS_CSS)
        for product in products :
            name = product.css('.product-name ::text').get()
            price = product.css('.product-price ::text').get().replace('$','')
            quantity = product.css('.product-quantity ::text').get()
            index_split=quantity.find('|')
            ppu = quantity[index_split+1:]

            amount = quantity[:index_split]
            ounces = self.collect_ounces(amount)
            unit = self.collect_unit(amount)
            

            print (f"yielding - {name}, {price}, {ppu}, {ounces}, {unit}")
            yield{
              "name": name,
              "price": price,
              "ounces": ounces,
              "unit": unit,
              "price-per-unit": ppu,
              "url": url,
              "section": section,
              "subsection": subsection
            }

   
        finish_url(self.conn,self.store_id,url)
    
    # @description collects and returns the ounces from the grocery
    # @param string - string to collect the ounces from
    # @returns 0 if no ounces could be detected - else returns the ounces 
    def collect_ounces(self,string):
        ret = 0
        FLOZ="fl oz"
        OZ="oz"
        LBAVG="lb (avg.)"
        LB="lb"
        quantity = re.findall("[0-9]+[.0-9]*",string)[0]
        if string.find(FLOZ) != -1:
            # oz != floz
            ret = 0
        elif string.find(OZ) != -1:
            ret = string.replace(OZ,'')
            ret = float(quantity)
        elif string.find(LBAVG) != -1:
            ret = string.replace(LBAVG,'')
            ret = float(quantity) * 16
        elif string.find(LB) != -1:
            ret = string.replace(LB, '')
            ret = float(quantity) * 16
        return ret

    # @description collects the units from the grocery
    # @param string - string to collect the units from
    # @returns - empty string if it can't find units. Else returns the units from the string
    def collect_unit(self,string):
        raw_units = re.findall("[A-Za-z/s]+",string)[0]
        unit = convert_units(raw_units)
        return unit