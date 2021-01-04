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
                  finish_url, get_next_pagination, is_url_scraped)

# TODO handle locatoin
# TODO continue midscrape


class walmartUrlSpider(scrapy.Spider):
    name = "walmart_url_spider"
    store_name = "walmart"
    start_urls = ['https://www.walmart.com/grocery']
    location = "8386 Sudley Road"
    """
    These are intialized in pipelines.py
    """
    conn = ""
    cursor = ""
    store_id = -1
    NEXT_BUTTON_SELECTOR = '[data-automation-id="nextButton"]'
    PAGE_STRING = "&page="

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
        url = response.url
        self.logger.info(f"about to call walk_menu with response.url: {url}")
        request = create_unfiltered_parse_request(response.url, self.walk_menu, EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-automation-id="NavigationBtn"]')), meta_url=response.url)
        if is_url_scraped(self.cursor, url, scrape_urls=True):
            next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                    scrape_urls=True, filter="aisle=")
            request = create_parse_request(next_url,
                                           self.handle_pagination,
                                           EC.element_to_be_clickable(
                                                                     (By.CSS_SELECTOR, '[aria-current="page"]')),
                                           meta_url=next_url)
        yield request

    def walk_menu(self, response):
        self.logger.info('Inside walk_menu')
        start_url = self.driver.current_url
        menu_button = self.driver.find_element_by_css_selector(
            '[data-automation-id="NavigationBtn"]')
        menu_button.click()

        time.sleep(.5)

        departments = self.driver.find_elements_by_css_selector(
            '.NavigationPanel__department___1DF7d button')
        for department in departments:
            department_name = department.get_attribute('aria-label')
            department.click()
            time.sleep(.5)
            aisles = self.driver.find_elements_by_css_selector(
                '.NavigationPanel__aisleLink___309i2')
            for aisle in aisles:
                url = aisle.get_attribute('href')
                aisle_name = aisle.get_attribute('innerText')
                # self.department_name = department_name
                # self.aisle_name = aisle_name
                self.logger.info(
                    f"department_name: {department_name}, aisle_name: {aisle_name}")
                category = lookup_category("", department_name, aisle_name)
                self.logger.info(f"Storing aisle: {aisle_name}, url: {url}")
                store_url(self.conn, url, self.store_id,
                          category, department_name, aisle_name)

        finish_url(self.conn, self.store_id, start_url, scrape_urls=True)
        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                scrape_urls=True, filter="aisle=")

        self.next_url = next_url
        pagination_request = create_parse_request(next_url,
                                                  self.handle_pagination,
                                                  EC.element_to_be_clickable(
                                                      (By.CSS_SELECTOR, '[aria-current="page"]')),
                                                  meta_url=next_url)

        yield pagination_request

    def handle_pagination(self, response):
        self.logger.info('inside handle_pagination')
        url = self.driver.current_url
        next_button = self.driver.find_elements_by_css_selector(
            self.NEXT_BUTTON_SELECTOR)
        if len(next_button) != 0:
            next_page_url = get_next_pagination(
                self.PAGE_STRING, url)
            metadata = get_url_metadata(self.cursor, url)
            category = metadata[0]
            section = metadata[1]
            subsection = metadata[2]
            quantity = self.driver.find_element_by_css_selector(
                '.Title__browseTotalCount___OWylh').get_attribute('innerText')
            quantity = re.findall('[0-9]+', quantity)[0]
            store_url(self.conn, next_page_url, self.store_id,
                      category, section, subsection, grocery_quantity=quantity)

        finish_url(self.conn, self.store_id, url, scrape_urls=True)
        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                scrape_urls=True, filter="aisle=")
        request = create_parse_request(next_url,
                                       self.handle_pagination,
                                       EC.element_to_be_clickable(
                                           (By.CSS_SELECTOR, '[aria-current="page"]')),
                                       meta_url=next_url)
        yield request
