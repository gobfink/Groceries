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

class safewayUrlScraper(scrapy.Spider):
    name = "safeway_url_spider"
    store_name = "safeway"
    start_urls = ["https://www.safeway.com/shop/aisles.1431.html"]
    base_url = "https://www.safeway.com"

    section_dict = {}
    urls = []
    processedUrls = []
    location = "12821 Braemar Village Plaza"
    zipcode = "20136"
    page_str="?sort=&page="
    # For some reason all the urls
    default_store_number="3132"
    store_number=0


    # @description the start function for the scraper. Kicks off the scraping
    def start_requests(self):
        url = self.start_urls[0]
        location_request = create_parse_request(url,
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

        url = self.driver.current_url
        self.store_number = str(re.findall(r'\d{4}',url)[0])
        print(f"Setting store number to - {self.store_number}")

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
        scrape_request = create_unfiltered_parse_request(response.url,
                                                         self.run,
                                                         EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))

        yield scrape_request

    # @description scrapes the urls from the response and stores in the database
    # @param response - html response of the webpage
    def scrape_urls(self,response):
        # FIXME the links for the hrefs default to 3132 then change to the correct 2635

        mainGroups = response.css('.col-12.col-sm-12.col-md-4.col-lg-4.col-xl-3')
        section = response.css('[aria-current="location"] ::text').get()
        if section is not None:
            section = section.strip()
        print("Inside scrape_urls")
        #TODO can probably infer some categories from location
        for mainGroup in mainGroups:
            #print (f"Using mainGroup - {mainGroup}")
            #It might be coming from here? it looks like the main categories are all having issues
            view_all = mainGroup.css('.text-uppercase.view-all-subcats ::attr(href)').get()
            view_all_url = self.base_url + view_all
            view_all_url = view_all_url.replace(self.default_store_number, self.store_number)
            section = mainGroup.css('.product-title.text-uppercase ::text').get()
            section = section.strip()
            category = lookup_category("",section,"")
            print (f"view_all_url - {view_all_url}, section - {section}, category - {category}")
            store_url(self.conn,view_all_url,self.store_id, category,section,"")

        aisleCategories = response.css('a.aisle-category')
        for aisleCategory in aisleCategories:
            aisleName = aisleCategory.css('::attr(data-aisle-name)').get().strip()
            aisleHref = aisleCategory.css('::attr(href)').get()
            aisleUrl = self.base_url + aisleHref
            aisleUrl = aisleUrl.replace(self.default_store_number, self.store_number)
            subsection = aisleName
            category = lookup_category("",section,subsection)
            print (f"found aisleCategory with section - {section}, subsection - {subsection} ")
            store_url(self.conn,aisleUrl,self.store_id,category,section,subsection)

        siblingAisles = response.css('.siblingAisle')
        for siblingAisle in siblingAisles:
            print (f"using siblingAisle - {siblingAisle}")
            href = siblingAisle.css('::attr(href)').get()
            siblingAisleUrl = self.base_url + href
            siblingAisleUrl = siblingAisleUrl.replace(self.default_store_number, self.store_number)
            section = response.css('[aria-current="location"] ::text').get()
            section = section.strip()
            subsection = siblingAisle.css('::text').get()
            subsection = subsection.strip()
            category = lookup_category("",section,subsection)
            print(f"siblingAisle storing: {siblinAisleUrl}")
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
            next_page_url = next_page_url.replace(self.default_store_number, self.store_number)
            print (f'load-more-button. storing - {next_page_url}, section - {section}, subsection - {subsection}, category - {category}')
            store_url(self.conn,next_page_url,self.store_id,category,section,subsection)
    # @description first scrapes the urls, then goes through and parses the groceries from the webpage
    # @param response - html response of the webpage
    def run(self, response):
        page_1_str=self.page_str+"1"
        meta_url = response.meta.get("url")
        #Basically the website redirects us to the url and page_1_str, which isn't added to our database
        # So we trim that off so we can get the url in our database
        this_url = trim_url(response.url,page_1_str)
        print (f"inside run for {this_url}, meta_url: {meta_url}")
        if meta_url != this_url:
            print (f"meta_url: {meta_url} !=  response.url: {response.url}, therefore it must be invalid - skipping")
            this_url = meta_url
        else :
            self.scrape_urls(response)

        finish_url(self.conn,self.store_id,this_url,True)
        print("finishing url - " + this_url)
        next_url = get_next_url(self.cursor, 1, self.store_id,True)
        if next_url is None:
            print ("Next url is none therefore we must be finished ! ")
            return
        else:
            next_request = create_unfiltered_parse_request(next_url,
                                                self.run,
                                                EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
        print(f"got next_url - {next_url}")

        yield next_request
