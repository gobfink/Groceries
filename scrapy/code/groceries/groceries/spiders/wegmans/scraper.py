#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from util import convert_dollars, convert_units, lookup_category, clean_string, convert_to_ounces, convert_ppu
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
import MySQLdb
import datetime
import time

class wegmansScraper(scrapy.Spider):
    name = "wegmans_spider"
    store_name = "wegmans"  
    start_urls = ['https://shop.wegmans.com/shop/categories/470','https://shop.wegmans.com/shop/categories']
    base_url = "https://shop.wegmans.com"
    #location = "LAKE MANASSAS"
    location = "FAIRFAX"
    queried_location=""
    section_dict = {}
    urls = []
    processedUrls = []
    conn = ""
    store_id=-1

    def get_url_metadata(self,url):
        sql=f"SELECT category, section, subsection FROM urlTable WHERE url=\"{url}\""
        print(f'get_url_metadata - {sql}')
        cursor=self.conn.cursor()
        cursor.execute(sql)
        metadata=cursor.fetchone()
        return (metadata)

    def get_next_url(self,iteration):
        sql=f"SELECT url from urlTable WHERE scraped=0 ORDER BY updated DESC LIMIT {iteration}"
        self.cursor.execute(sql)
        url=self.cursor.fetchone()
        if url is None:
            return None
        else:
            url=url[0]
            return url



    def store_url(self,url,category,section,subsection):
        time=datetime.datetime.now()
        store_query=f"SELECT Hits FROM urlTable where url='{url}' AND store_id='{self.store_id}'"
        cursor = self.conn.cursor()
        cursor.execute(store_query)
        hits=cursor.fetchone()
        if hits is None:
            store_url_sql = f"INSERT INTO urlTable (url, store_id, scraped, Updated, category, section, subsection, hits) VALUES (\"{url}\",{self.store_id},0,\"{time}\",\"{category}\",\"{section}\",\"{subsection}\",1);"
            #print (f"store_url_sql - {store_url_sql}")
            self.cursor.execute(store_url_sql)
            self.conn.commit()
        else:
            hits=hits[0]+1
            update=f" UPDATE urlTable SET hits={hits} WHERE url='{url}' AND store_id='{self.store_id}'"
            #print(f"update - {update}")
            self.cursor.execute(update)
            self.conn.commit()            

    def finish_url(self,url):
        url_update=f" UPDATE urlTable SET scraped=1 WHERE url=\"{url}\" AND store_id='{self.store_id}'"
        self.cursor.execute(url_update)
        self.conn.commit()
        return url
    def create_parse_request(self,url,callback,wait_until):
        request = SeleniumRequest(
                    url=url,
                    callback=callback, 
                    wait_time=50, 
                    wait_until=wait_until
                    )

        return request

    def start_requests(self):
        store_query=f"SELECT id FROM storeTable where name='{self.store_name}' AND location='{self.location}'"
        self.cursor = self.conn.cursor()
        self.cursor.execute(store_query)
        self.store_id=self.cursor.fetchone()[0]

        if len(self.start_urls) != 0:
            url = self.start_urls.pop()
            self.store_url(url,"","","")
            print(f"Starting requests with - {url}")
            wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-test="store_button"]'))
            request = self.create_parse_request(url,self.parse_urls,EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="store-button"]')))
            #request = self.create_parse_request(url,self.parse_urls,wait_until)
            yield request

        else:
            print("start_requests - len(start_urls) == 0 : exiting")

    def update_location_db(self,location,store_id):
        store_update=f"UPDATE storeTable SET location=\"{location}\" WHERE id=\"{store_id}\""
        self.cursor.execute(store_update)
        self.conn.commit()

    def change_store_location(self, response):
        time.sleep(10)
        self.driver=response.request.meta['driver']
        self.close=self.driver.find_element_by_css_selector('.close')
        self.close.click()
        store_url=self.driver.find_element_by_css_selector('[data-test="store-button"]')
        store_url.click()

        time.sleep(10)
        stores=self.driver.find_elements_by_css_selector('.store-row')
        # Go through each of the stores, until one matches the text, then click on it
        for store in stores:
            name=store.find_element_by_css_selector('.name')
            #print (f"change_store_location - {name.text}")
            if name.text == self.location:
                button = store.find_element_by_css_selector('.button.small.hollow')
                self.button=button
                #print (f"clicking element - {button.text}")

                #inspect_response(response,self)
                button.click()
                time.sleep(5)
                self.queried_location = self.driver.find_element_by_css_selector('[data-test="store-button"]').text
                print("set location - " + self.queried_location)
                self.update_location_db(self.queried_location,self.store_id)
                return


    def parse_urls(self, response):
        location = response.css('[data-test="store-button"] ::text').get()
        self.driver=response.request.meta['driver']
        location = self.driver.find_element_by_css_selector('[data-test="store-button"]').text
        print(f"detected location - {location}")
        if location != self.location:
            self.change_store_location(response)

        self.section_group = response.css(".subcategory.category")
        section_group = response.css(".subcategory.category")
        for section in section_group:
            section_name = section.css(".css-1pita2n ::text").get()
            url_nodes = section.css("ul.children a")
            for url_node in url_nodes:
                subsection_name = url_node.css("::text").get() 
                url = self.base_url + url_node.css("::attr(href)").get()

                self.store_url(url, lookup_category("",section_name,subsection_name) ,section_name, subsection_name)


        self.finish_url(response.url)

        if len(self.start_urls) != 0:
            next_url=self.start_urls.pop()
            self.store_url(next_url, "","","")
            request = self.create_parse_request(next_url,self.parse_urls,EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="store-button"]')))

        else:
            next_url=self.get_next_url(1)
            request = self.create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR, '[add-to-cart]')))

        if next_url is None:
            print ("No more URLs to parse. Finishing")
            return
        #FIXME these try except blocks don't actually handle timeout exceptions from navigating to the wrong url
        try:
            yield request
        except:
            print (f"Parse -  Errored out processing request for - {next_url} ")
            next_url=self.get_next_url(2)
            print (f"Parse - Now handling {next_url}")
            request = self.create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR, '[add-to-cart]')))
            yield request

    def parse(self, response):


        url=response.url
        self.finish_url(url)
        items = response.css('.cell-content-wrapper')
        metadata=self.get_url_metadata(url)
        section=metadata[1]
        subsection=metadata[2]
        #check if it has a next button,
        next_page=response.css('.pagination-next:not(.disabled)').get()
        if next_page is not None:
            #inspect_response(response,self)
            page_string="?page="
            page_str_len=len(page_string)
            i = url.find(page_string)
            #if yes, check url if it has a page part on it
            if i == -1:
            #if no, add ?page=2 to it
                next_url = url + page_string+"2"
            else:
            #if yes, extract page and add 1 
                page_number = i+page_str_len
                current_page = int(url[page_number:])
                next_page = current_page + 1
                next_url = url[:page_number] + str(next_page)
            #then add to self.urls
            self.store_url(next_url, lookup_category("",section,subsection) ,section, subsection)


        
        for item in items:
            name=item.css('.cell-title-text ::text').get()
            name=clean_string(name,['\"'])
            price=item.css('[data-test="amount"] .css-19m8h51 ::text').get()
            price=convert_dollars(price)
            
            quantity=item.css('[data-test="amount"] .css-cpy6p ::text').get()

            ounces=item.css('.cell-product-size ::text').get()
            ounces=convert_to_ounces(ounces)

            ppu=item.css('[data-test="per-unit-price"] ::text').get()
            ppu=convert_ppu(ppu)

            print(f"name - {name}, price - {price}, quantity - {quantity}, ounces - {ounces}, ppu - {ppu}, url - {url}, section - {section}, subsection - {subsection} ")
            #inspect_response(response,self)
            yield {
                "name": name,
                "price": price,
                "ounces": ounces,
                "price-per-unit": ppu,
                "url": url,
                "section": section,
                "subsection": subsection
            }
        
        next_url = self.get_next_url(1)
        if next_url is None:
            print ("No more URLs to parse. Finishing")
            return
        request = self.create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR, '[add-to-cart]')))

        if next_url is not None:
            try:
                yield request
            except:
                print (f"Parse -  Errored out processing request for - {next_url} ")
                next_url=self.get_next_url(2)
                print (f"Parse - Now handling {next_url}")
                request = self.create_parse_request(next_url,self.parse,EC.element_to_be_clickable((By.CSS_SELECTOR, '[add-to-cart]')))
          
            yield SeleniumRequest(
                    url=next_url,
                    callback=self.parse,
                    wait_time=50,
                    wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.full.cart.add'))
                    )

