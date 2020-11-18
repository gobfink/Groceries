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
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


from seleniumHelpers import create_parse_request, create_unfiltered_parse_request
import time
import re

from util import (read_script, store_url, get_next_url,
                  get_url_metadata, lookup_category, finish_url, get_next_pagination,
                  trim_url, convert_to_ounces, convert_units, clean_string, 
                  is_section_in_store_id, is_subsection_in_store_id)



class harristeeterUrlScraper(scrapy.Spider):
    name = "harris-teeter-url_spider"
    store_name = "harris-teeter"
    start_urls = ["https://www.harristeeter.com/shop/store/313"]
    base_url = start_urls[0]

    #section_dict = {}
    #urls = []
    #processedUrls = []
    location = "10438 Bristow Center Dr"
    zipcode = "20136"
    page_str="?sort=&page="
    delay=10


    # @description the start function for the scraper. Kicks off the scraping
    def start_requests(self):
        print("inside start_requests")

        scrape_url_request = create_parse_request(self.start_urls[0],
                                                self.crawl_menu,
                                                EC.element_to_be_clickable((By.CSS_SELECTOR,'.nav-open')))
        yield scrape_url_request


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
                                                             EC.element_to_be_clickable((By.CSS_SELECTOR,'.add-product [role="button"]')))     
        else:
            scrape_request = create_unfiltered_parse_request(response.url,
                                                             self.parse,
                                                             EC.element_to_be_clickable((By.CSS_SELECTOR,'#openFulfillmentModalButton')))
   
        yield scrape_request

    # @desscription - crawls the main menu - basically in order to pull the urls it needs to click each link
    def crawl_menu(self,response):
        self.driver=response.request.meta['driver']
        actions = ActionChains(self.driver)
        print("inside crawl_menu")

        accept_cookies = self.driver.find_element_by_css_selector('[title="Accept Cookies"]')
        self.handle_click(accept_cookies,self.delay)
        menu_button = self.driver.find_element_by_css_selector('.nav-open')
        self.handle_click(menu_button,self.delay)
        #We then need to scrape all of the (.'category-link') and then hover over each one and scrape the hrefs that appear
        sections=self.driver.find_elements_by_css_selector('.category-link')
        next_section = self.get_next_section(sections)
        self.section_list = sections

        #inspect_response(response,self)
        while next_section is not None:
            actions.move_to_element(next_section)
            section_name = next_section.get_attribute('innerText')
            print(f"using next_section: {section_name}")
            self.handle_click(next_section,self.delay)

            current_url = self.driver.current_url
            category = lookup_category("",section_name,"")
            #While on this page we need to click on all of the subsections
            self.crawl_submenu(response,section_name)
            #inspect_response(response,self)

            num_groceries=self.get_quantity()
            store_url(self.conn,current_url,self.store_id,category,section_name,"",num_groceries)
            # Now we need to reset it and do it again
            self.handle_click(menu_button,self.delay)
            sections=self.driver.find_elements_by_css_selector('.category-link')
            next_section = self.get_next_section(sections)
        return

    # @description returns the first section from the list that is not not in the url table with the inherient store_id, returns None if the whole list is
    # @param section_list list of webelemnts to look at the innerText for and compare with the sections 
    # @returns first webelement whos innerText is not a section in the urlTable for the given store or None if all of them match
    def get_next_section(self,section_list):
        ret = None

        for section in section_list:
            current_section = section.get_attribute('innerText')
            in_store_id = is_section_in_store_id(self.cursor, self.store_id, current_section)
            print (f"get_next_section: in_store_id - {in_store_id} for section - {current_section}")
            if (not in_store_id):
                ret = section
                break


        return ret

    # @description crawls a submenu (1 level deep) for a particular entry and adds the urls to the urlTable
    # @param httpresponse response - response from a yield call for scrapy only used for inspect_response calls
    # @param string section - section that its crawling for
    def crawl_submenu(self,response,section):
        ret = None
        subsections=self.driver.find_elements_by_css_selector('#collapseOne > li > a')
        next_subsection = self.get_next_subsection(section,subsections)

        while next_subsection is not None:
            current_subsection = next_subsection
            subsection_text = current_subsection.get_attribute('innerText')

            self.handle_click(current_subsection,self.delay)

            try:
                #From here we should check if we are in a different menu
                clicked_element = self.driver.find_element_by_css_selector('#collapseOne > li > span')
            except NoSuchElementException:
                clicked_element = None
            
            if clicked_element is None:
                #print(f"Now entered submenu for {subsection_text}")
                self.crawl_2nd_layer_menu(section,subsection_text)
            else:
                #print(f"Not in submenu for {subsection_text}")
                current_url = self.driver.current_url
                category = lookup_category("",section,subsection_text)
                num_groceries = self.get_quantity()
                self.walk_through_pages(section,subsection_text)
                store_url(self.conn,current_url,self.store_id,category,section,subsection_text,num_groceries)
            #inspect_response(response,self)
            #print (f"subsection_text - {subsection_text}")
            local_subsections=self.driver.find_elements_by_css_selector('#collapseOne > li > a')
            next_subsection = self.get_next_subsection(section,local_subsections)
        return ret

    # @description returns the first section from the list that is not not in the url table with the inherient store_id, returns None if the whole list is
    # @param section - section to search for the subsections 
    # @param subsection_list list of webelemnts to look at the innerText for and compare with the subsections 
    # @returns first webelement whos innerText is not a subsection in the urlTable for the given store or None if all of them match
    def get_next_subsection(self,section,subsection_list):
        ret = None

        for subsection in subsection_list:
            current_subsection = subsection.get_attribute('innerText')
            in_store_id = is_subsection_in_store_id(self.cursor, self.store_id, section, current_subsection,'%pageNo%')
            print (f"get_next_subsection: in_store_id - {in_store_id}, section - {section}, for subsection - {current_subsection}")
            if (not in_store_id):
                ret = subsection
                break
        return ret

    # @desscription crawls a second layer menu (sometimes when you click on a subsection you get another menu) and adds the urls to the urlTable database
    # @param string section - section that its crawling
    # @param string subsection - subsection that it is crawling 
    def crawl_2nd_layer_menu(self,section,subsection):
        section_url=self.driver.current_url
        section_category = lookup_category("",section,subsection)

        #print (f"inside crawl_2nd_layer_menu for {section}:{subsection} with url - {section_url}")

        sections=self.driver.find_elements_by_css_selector('#collapseOne > li > a')
        next_section = self.get_next_2nd_layer_section(section,subsection,sections)


        while next_section is not None:
            current_section = next_section
            section_text = current_section.get_attribute('innerText')
            #The trick here is that for 2nd layer sections is to append the layer2 info on the subsection
            subsection_text = subsection +": "+section_text

            self.handle_click(current_section,self.delay)


            #print (f"subsection_text - {subsection_text}")
            current_url = self.driver.current_url
            category = lookup_category("",section,subsection_text)
            num_groceries = self.get_quantity()
            #We'll need to handle the pagination here, because we don't revisit this spot
            self.walk_through_pages(section,subsection_text)
            store_url(self.conn,current_url,self.store_id,category,section,subsection_text,num_groceries)
            sections=self.driver.find_elements_by_css_selector('#collapseOne > li > a')
            next_section = self.get_next_2nd_layer_section(section,subsection,sections)

        #Store the section url after so we know we've completed it
        store_url(self.conn,section_url,self.store_id,section_category,section,subsection,self.get_quantity())
        #We then need to click on the section header to get back outside the menu and continue on
        section_button = self.driver.find_element_by_css_selector('li.breadcrumb-item:nth-child(2) > span:nth-child(1) > a:nth-child(1)')
        self.handle_click(section_button,self.delay)

    # @description returns the first section from the list that is not not in the url table with the inherient store_id, returns None if the whole list is
    # @param section - section to search for the subsections
    # @param subsection - subsection to prepend the search term with 
    # @param layer2_sections list of webelemnts to look at the innerText for and compare to see if its inside the list 
    # @returns first webelement whos innerText is not a `<subsection>: <innerText>` in the urlTable for the given store or None if all of them match
    def get_next_2nd_layer_section(self,section,subsection,layer2_sections):
        ret = None
        for layer2 in layer2_sections:
            section_name = layer2.get_attribute('innerText')
            subsection_text = subsection + ": " +section_name
            #For some reason this isn't saving the state when interupted during pagination
            is_section_in_store_id = is_subsection_in_store_id(self.cursor,self.store_id,section,subsection_text,"%pageNo%")
            print (f"get_next_2nd_layer_section: in_store_id - {is_section_in_store_id}, section - {section}, for subsection - {subsection_text}")
            if (not is_section_in_store_id):
                ret = layer2
                break
        return ret

    # @description walks through the subpages for the current url and adds them to the url database
    # @param section - section to store the urls under
    # @param subsection - subsection to store the urls under
    def walk_through_pages(self,section,subsection):
        #print(f"walk_through_pages for {section},{subsection}")
        category = lookup_category("",section,subsection)
        start_url = self.driver.current_url
        try:
            #From here we should check if we are in a different menu
            next_arrow = self.driver.find_element_by_css_selector('.next-arrow')
        except NoSuchElementException:
            return
        self.handle_click(next_arrow,self.delay)
        current_url = self.driver.current_url
        store_url(self.conn,current_url,self.store_id,category,section,subsection,self.get_quantity())
        #Unfortunately we want to recurse until their is no more pages to walk through
        self.walk_through_pages(section,subsection)


    # @description returns the quanity of items in a subsection or 0if it can't detect it
    # @returns int quantity - quantity of items for the subsection 
    def get_quantity(self):
        quantity_selector = ("body > app-root > div > hts-layout > span > hts-shop-by-category > div > " 
                            "section > div > div.product-category-list.col-lg-7.col-md-9.column7 >  "
                            "div.smart-filter.clearfix > h2 > span")
        ret = 0
        try:
            quantity = self.driver.find_element_by_css_selector(quantity_selector).text
            quantity = clean_string(quantity,['(',')'])
            if ret is None:
                ret = 0
            ret = int(quantity)
        except NoSuchElementException:
            ret = 0
        print(f"in get_quantity - found quantity of {ret}")
        return ret
        
    # @description handles the attempted clicks and adds more time if it hits a timeout or nosuchelement exception
    # @param htmlelement clickme - element to click
    # @param int waittime - time to wait
    def handle_click(self, clickme, waittime):
        try:
            clickme.click()
            time.sleep(waittime)
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print (f"sleeping trying to click -  {clickme} and hit exception {e}")
            time.sleep(waittime)
            self.handle_click(clickme,waittime)
    