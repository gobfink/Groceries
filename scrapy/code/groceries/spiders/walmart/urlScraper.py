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
        walk_menu_request = create_unfiltered_parse_request(response.url, self.walk_menu, EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-automation-id="NavigationBtn"]')), meta_url=response.url)
        yield walk_menu_request
        # self.walk_menu(response)

    def walk_menu(self, response):
        self.logger.info('Inside walk_menu')
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

        next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
                                scrape_urls=True, filter="aisle=")

        self.next_url = next_url
        pagination_request = create_unfiltered_parse_request(next_url,
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
# mainSearchContent > div.ProductsPage__paginator___1slAl
# FIXME convert this to a yield and wait for the actual elements to load
#
#        while next_url is not None:
#            url = next_url
#            request = create_parse_request(url,
#                                           self.handle_pagination,
#                                           EC.visibility_of(
#                                               (By.CSS_SELECTOR, '[data-automation-id="onboardingModalCloseBtn"]')),
#                                           meta_url=url)
#            self.driver.get(url)
#            next_button = self.driver.find_elements_by_css_selector(
#                NEXT_BUTTON_SELECTOR)
#            if len(next_button) != 0:
#                next_page_url = get_next_pagination(
#                    PAGE_STRING, self.driver.url)
#                metadata = get_url_metadata(self.cursor, url)
#                category = metadata[0]
#                section = metadata[1]
#                subsection = metatdata[2]
#                next_page_url = get_next_pagination(page_string, url)
#                store_url(self.conn, next_page_url, self.store_id,
#                          category, section, subsection, scrape_urls=True)
#
#            finish_url(self.conn, self.store_id, url, scrape_urls=True)
#            next_url = get_next_url(self.cursor, 1, store_id=self.store_id,
#                                    scrape_urls=True, filter="aisle=")

        # TODO finish converting this over to selenium
        # TODO also have this check and update the location
    def scrape_urls(self, response):
        # 1. sort through data and extract urls
        # 2. put urls together
        # 3. Loop to each url, returning @parse
        base_url = "https://www.walmart.com"
        self.raw = response.body_as_unicode()
        # print("raw: " + self.raw)
        remove = ['{', '}', 'Link', ' ']
        self.cleaned = self.raw
        for char in remove:
            self.cleaned = self.cleaned.replace(char, '')
        self.comma_split = self.cleaned.split('","')
        # print ("cleaned - " + cleaned)
        # print ("comma_split - " )
        # print (*comma_split)
        self.colon_split = [entry.split('":"') for entry in self.comma_split]
        # inspect_response(response, self)
        self.colon_split[0].remove('"sections')
        # print ("colon_split - ")
        # print (*colon_split)
        self.urls = [entry[-1] for entry in self.colon_split]
        # print("urls - ")
        # print(self.urls)

        section = "unset"
        subsection = "unset"

        self.section_dict = {}
        chars_to_remove = ["\'", "&"]
        for entry in self.colon_split:

            # each entry will have a subheading (normally at 0 unless it has a heading entry)
            section = clean_string(entry[0], chars_to_remove)
            url_end = clean_string(entry[-1], "\"")

            # if its a section header it will contain 3 entries
            #   and all subsequent entries will have the same heading
            if len(entry) > 2:
                section = clean_string(entry[0], chars_to_remove)
                subsection = clean_string(entry[1], chars_to_remove)

            url = base_url + url_end
            category = lookup_category("", section, subsection)
            store_url(self.conn, url, self.store_id, category,
                      section, subsection, scrape_urls=True)
            # self.section_dict[url] = (self.section, self.subsection)

            # print(section, subsection, url)

        next_url = get_next_url(
            self.cursor, 1, store_id=self.store_id, scrape_urls=True)
        if next_url is None:
            print("No more urls to parse finishing")
        else:
            yield SplashRequest(next_url,
                                self.scrape_next_url,
                                endpoint='render.html',
                                args={
                                    'wait': 10,
                                    'section': section,
                                    'subsection': subsection
                                })

    def scrape_next_url(self, response):
        NEXT_BUTTON = '[data-automation-id="nextButton"]'
        # Handle pagination
        url = response.url
        print(f"working on url - {url}")
        metadata = get_url_metadata(self.cursor, url)
        section = metadata[1]
        subsection = metadata[2]

        next_page = response.css(NEXT_BUTTON).get()

        if next_page is not None:
            # inspect_response(response,self)
            page_string = "&page="
            page_str_len = len(page_string)
            next_page_url = get_next_pagination(page_string, url)

            store_url(self.conn, next_page_url, self.store_id, lookup_category(
                "", section, subsection), section, subsection, scrape_urls=True)

        finish_url(self.conn, self.store_id, url, scrape_urls=True)
        next_url = get_next_url(
            self.cursor, 1, store_id=self.store_id, scrape_urls=True)

        print(f"next_url - {next_url}")
        if next_url is None:
            print("No more urls - finishing")
        else:
            yield SplashRequest(next_url,
                                self.parse,
                                endpoint='render.html',
                                args={
                                    'wait': 10,
                                    'section': section,
                                    'subsection': subsection
                                })
