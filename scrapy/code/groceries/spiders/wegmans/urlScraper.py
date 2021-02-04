#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from util import (convert_dollars, convert_units, lookup_category, clean_string,
                  convert_to_ounces, convert_ppu, get_next_url, store_url,
                  finish_url, get_url_metadata, is_url_scraped,
                  find_store_id, update_location_db)
from seleniumHelpers import (create_parse_request,
                             create_unfiltered_parse_request)

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
from wegmans_utils import (close_modal, change_store_location)

import MySQLdb
import time


class wegmansUrlScraper(scrapy.Spider):
    name = "wegmans_url_spider"
    store_name = "wegmans"
    start_urls = ['https://shop.wegmans.com/shop/categories']

    base_url = "https://shop.wegmans.com"
    location = "LAKE MANASSAS"
    #location = "FAIRFAX"
    queried_location = ""
    section_dict = {}
    urls = []
    processedUrls = []
    """
    These are intialized in pipelines.py
    """
    conn = ""
    cursor = ""
    store_id = -1
    delay = 10
    page_string = "?page="

    def start_requests(self):
        url = self.start_urls[0]
        request = create_unfiltered_parse_request(url,
                                                  self.collect_menu,
                                                  EC.element_to_be_clickable(
                                                      (By.CSS_SELECTOR, '[id="catalog-nav-main-shop.categories"]')),
                                                  meta_url=url
                                                  )

        if is_url_scraped(self.cursor, url, self.store_id, scrape_urls=True):
            next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                    scrape_urls=True,filter=self.page_string,reverse_filter=True)


            request = create_unfiltered_parse_request(next_url,
                                           self.handle_first_request,
                                           EC.element_to_be_clickable(
                                               (By.CSS_SELECTOR, '#shopping-selector-parent-process-modal-close-click')),
                                           meta_url=next_url,
                                           errback=self.handle_pagination
                                           )

        store_url(self.conn, url, self.store_id, "Start", "", "")
        yield request

    def handle_first_request(self,response):
        self.logger.info(f"handling first request. {response.url}")
        self.driver = response.request.meta['driver']
        close_modal(self)
        self.change_store_location()
        self.logger.info(f"about to create create_unfiltered_parse_request for {response.url}")
        request = create_unfiltered_parse_request(response.url,
                                       self.handle_pagination,
                                       EC.element_to_be_clickable(
                                           (By.CSS_SELECTOR, '.pagination-page.pager-item')),
                                       meta_url=response.url,
                                       errback=self.no_pagination
                                       )
        yield request


    def collect_menu(self, response):
        self.logger.info("inside collect_menu! ")
        self.driver = response.request.meta['driver']
        close_modal(self)
        change_store_location(self)
        departments = self.driver.find_elements_by_css_selector(
            '[category-filter="subcategory"]')
        for department in departments:
            dept_name = department.find_element_by_css_selector(
                '[data-test="category-card-"]').text
            aisles = department.find_elements_by_css_selector('a')
            self.logger.info(f"dept_name: {dept_name}")
            self.aisles = aisles
            for aisle in aisles:
                aisle_name = aisle.text
                aisle_url = aisle.get_attribute("href")
                category = lookup_category("", dept_name, aisle_name)
                store_url(self.conn, aisle_url, self.store_id,
                          category, dept_name, aisle_name)
            #inspect_response(response, self)

        self.logger.info("finished collect_menu! ")
        finish_url(self.conn, self.store_id, response.url, scrape_urls=True)

        request = self.get_next_request()
        yield request

    def handle_pagination(self, response):
        # if it has a page-last class, read that content, and interprolate
        # else, get the last pager, page and interprolate
        self.logger.info("Inside handle_pagination")
        close_modal(self)
        change_store_location(self)
        base_url = response.url
        string_location=base_url.find(self.page_string)
        if string_location != -1:
            base_url = base_url[:string_location]
        pag_last = self.driver.find_elements_by_css_selector(
            '.pagination-last.pager-item')
        if pag_last:
            final_page_number = pag_last[0].text
        else:
            last_page = self.driver.find_elements_by_css_selector(
                '.pagination-page.pager-item')[-1]
            final_page_number = last_page.text

        final_page_number = int(final_page_number)
        metadata = get_url_metadata(self.cursor, base_url)

        category = metadata[0]
        section = metadata[1]
        subsection = metadata[2]

        for page_num in range(1, final_page_number+1):
            # Something like -
            # https://shop.wegmans.com/shop/categories/94 ?page= 13
            page_url = base_url + self.page_string + str(page_num)
            store_url(self.conn, page_url, self.store_id,
                      category, section, subsection)

        self.logger.info(f"finished handling pagination for {base_url}")
        finish_url(self.conn, self.store_id, response.url, scrape_urls=True)
        request = self.get_next_request()
        yield request

    def no_pagination(self, failure):
        url = failure.request.url
        self.logger.info(f"no_pagination for url: {url}, continuing")

        finish_url(self.conn, self.store_id, url, set_val=2, scrape_urls=True)
        # TODO add a filter so we don't get the ones with ?page=
        request = self.get_next_request()
        yield request

    def get_next_request(self):
        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                scrape_urls=True,filter=self.page_string,reverse_filter=True)

        request = create_parse_request(next_url,
                                       self.handle_pagination,
                                       EC.element_to_be_clickable(
                                           (By.CSS_SELECTOR, '.pagination-page.pager-item')),
                                       meta_url=next_url,
                                       errback=self.no_pagination
                                       )
        return request

#    def close_modal(self):
#        close_button = self.driver.find_elements_by_css_selector(
#            '#shopping-selector-parent-process-modal-close-click')
#        if close_button:
#            self.logger.info("Closing modal")
#            close_button[0].click()
#            time.sleep(.5)
#        else:
#            self.logger.info("No Modal detected continuing")
#
#    def change_store_location(self):
#        store_button = self.driver.find_element_by_css_selector(
#            '[data-test="store-button"]')
#        current_store = store_button.text
#        if current_store == self.location:
#            self.logger.info(
#                f"Current location = {current_store} is correct. Continuing.")
#            return
#        store_button.click()
#        time.sleep(self.delay)
#        stores = self.driver.find_elements_by_css_selector('.store-row')
#        # Go through each of the stores, until one matches the text, then click on it
#        for store in stores:
#            name = store.find_element_by_css_selector('.name')
#            store_name = name.text
#            #print (f"change_store_location - {name.text}")
#            if store_name == self.location:
#                button = store.find_element_by_css_selector(
#                    '[data-test="select-store-button"]')
#                button.click()
#                time.sleep(self.delay)
#                self.logger.info(f"Set location to {store_name}")
#                return

        self.logger.warn(f"Could not set location to {self.location}")
