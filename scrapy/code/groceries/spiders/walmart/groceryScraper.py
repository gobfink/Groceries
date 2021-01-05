#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumHelpers import (create_parse_request,
                             create_unfiltered_parse_request,
                             create_nocookies_request)
import time
import re

from util import (read_script, parse_float, lookup_category, get_next_url,
                  get_url_metadata, store_url, clean_string, handle_none,
                  finish_url, get_next_pagination)

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

class walmartGrocerySpider(scrapy.Spider):
    name = "walmart_grocery_spider"
    store_name = "walmart"
    start_urls = ['https://www.walmart.com/grocery']
    #FIXME actually implement location
    location="8386 Sudley Road"
    """
    These are intialized in pipelines.py
    """
    conn = ""
    cursor = ""
    store_id=-1

    #start_urls = ['https://www.target.com/c/grocery/-/N-5xt1a?Nao=0']
    def start_requests(self):
        url = self.start_urls[0]

        start_request = create_nocookies_request(url,
                                             self.handle_onboard,
                                             EC.element_to_be_clickable(
                                                 (By.CSS_SELECTOR, '[data-automation-id="onboardingModalCloseBtn"]')),
                                             meta_url=url)
        store_url(self.conn, url, self.store_id, "Start", "", "")
        yield start_request

    def handle_onboard(self, response):
        self.driver = response.request.meta['driver']
        self.logger.info("Handling Onboard modal")
        close_button = self.driver.find_element_by_css_selector(
            '[data-automation-id="onboardingModalCloseBtn"]')
        close_button.click()
        time.sleep(.5)
        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                scrape_urls=False, filter="aisle=")
        if next_url is None:
            self.logger.debug(
                    "Next_url is None therefore we must be finished!")
            return
        request = create_parse_request(next_url,
                                       self.parse,
                                       EC.element_to_be_clickable(
                                      (By.CSS_SELECTOR, '[aria-current="page"]')),
                                       meta_url=next_url)
        yield request

    def parse(self, response):
        url = response.url
        self.logger.info(f"Inside parse for {url}")

        GROCERY_SELECTOR = '[data-automation-id="productTile"]'
        SPONSORED_SELECTOR = '[data-automation-id="sponsoredProductTile"]'
        GROCERIES_SELECTOR = GROCERY_SELECTOR + ',' + SPONSORED_SELECTOR
        metadata=get_url_metadata(self.cursor,url)
        section=metadata[1]
        subsection=metadata[2]

        for grocery in response.css(GROCERIES_SELECTOR):
            NAME_SELECTOR = '[data-automation-id="name"] ::attr(name)'
            name = grocery.css(NAME_SELECTOR).extract_first()
            #parse the ounces off of the name
            decimal_regex = "([\d]+[.]?[\d]*|[.\d]+)"
            ounces = re.findall(decimal_regex + "\s*o(?:z|unces?)",
                                     name, re.IGNORECASE)
            pounds = re.findall(decimal_regex + "\s*(?:pound|lb)s?",
                                     name, re.IGNORECASE)
            count = re.findall("([\d]+)\s*(?:c(?:t|ount)|p(?:k|ack))",
                                    name, re.IGNORECASE)
            self.ounce = ounces
            self.pounds = pounds
            self.count = count
            #Check if the arrays returned from re.findall are empty
            if ounces:
                ounces = parse_float(ounces[0])
            else:
                ounces = 0
            if pounds:
                pounds = parse_float(pounds[0])
            else:
                pounds = 0
            if count:
                count = parse_float(count[0])
            else:
                count = 0

            if pounds != 0:
                ounces = 16*pounds
            elif count != 0:
                ounces *= count

            #            inspect_response(response,self)
            SALEPRICE_SELECTOR = '[data-automation-id="salePrice"] ::text'
            PRICE_SELECTOR = '[data-automation-id="price"] ::text'
            PRICE_PER_UNIT_SELECTOR = '[data-automation-id="price-per-unit"] ::text'

            name=grocery.css(NAME_SELECTOR).extract_first()
            name=clean_string(name,"\"")
            ounces=ounces
            pounds=pounds
            count=count
            price=str(handle_none(grocery.css(SALEPRICE_SELECTOR).extract_first())).replace('$','')
            ppu=convert_ppu(grocery.css(PRICE_PER_UNIT_SELECTOR).extract_first())

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
        next_url=get_next_url(self.cursor,1,store_id=self.store_id,filter="aisle=")

        print(f"next_url - {next_url}")
        if next_url is None:
            print ("No more urls - finishing")
        else:
            request = create_parse_request(next_url,
                                           self.parse,
                                           EC.element_to_be_clickable(
                                          (By.CSS_SELECTOR, '[aria-current="page"]')),
                                           meta_url=next_url)
            yield request
