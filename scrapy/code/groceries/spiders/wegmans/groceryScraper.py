#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from util import convert_dollars, convert_units, lookup_category, clean_string, convert_to_ounces, convert_ppu, get_next_url, store_url, finish_url, get_url_metadata, find_store_id, update_location_db
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
from wegmans_utils import (close_modal, change_store_location)
from seleniumHelpers import ( create_parse_request,
                              create_unfiltered_parse_request )
import MySQLdb
import time

class wegmansGroceryScraper(scrapy.Spider):
    name = "wegmans_grocery_spider"
    store_name = "wegmans"
    start_urls = ['https://shop.wegmans.com/shop/categories/470','https://shop.wegmans.com/shop/categories']
    base_url = "https://shop.wegmans.com"
    location = "LAKE MANASSAS"
    queried_location=""
    section_dict = {}
    urls = []
    processedUrls = []
    """
    These are intialized in pipelines.py
    """
    conn = ""
    cursor = ""
    store_id=-1
    delay = 10
    page_string = "?page="

    def get_next_request(self):
        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                filter=self.page_string)

        if next_url is None:
            self.logger.info("Could not find any more urls, therefore we must be finished!")
            return None

        request = create_parse_request(next_url,
                                   self.parse,
                                   EC.element_to_be_clickable(
                                       (By.CSS_SELECTOR, '[data-test="product-cell"]')),
                                   meta_url=next_url,
                                   errback=self.skip_page
                                   )
        return request

    def skip_page(self, failure):
        url = failure.request.url
        self.logger.info(f"skipping for url: {url}, continuing")
        finish_url(self.conn, self.store_id, url, set_val=-1)
        request = self.get_next_request()
        yield request

    def start_requests(self):
        request=self.get_next_request()
        yield request

    def parse(self, response):
        self.driver=response.request.meta['driver']
        close_modal(self)
        change_store_location(self)

        url=response.url
        metadata=get_url_metadata(self.cursor,url)
        section=metadata[1]
        subsection=metadata[2]
        #check if it has a next button,
        items = response.css('.cell-content-wrapper')
        for item in items:
            name=item.css('.cell-title-text ::text').get()
            name=clean_string(name,['\"'])
            price=item.css('[data-test="amount"] .css-19m8h51 ::text').get()
            price=convert_dollars(price)

            quantity=item.css('[data-test="amount"] .css-cpy6p ::text').get()

            unit=item.css('.cell-product-size ::text').get()
            ounces=convert_to_ounces(unit)

            ppu=item.css('[data-test="per-unit-price"] ::text').get()
            ppu=convert_ppu(ppu)

            self.logger.info(f"name - {name}, price - {price}, quantity - {quantity}, ounces - {ounces}, ppu - {ppu}, url - {url}, section - {section}, subsection - {subsection} ")
            #inspect_response(response,self)
            yield {
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

        request = self.get_next_request()
        yield request
