#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from util import convert_dollars, convert_units
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
import MySQLdb
import datetime



def convert_ppu(incoming_ppu):
    if incoming_ppu is None:
        return ""
    ppu = incoming_ppu
    charactersToRemove = ['$', '(',')']
    for remove in charactersToRemove:
        ppu = ppu.replace(remove,'')
    ppuSplit = ppu.split('/')
    cost = ppuSplit[0]

    units = ppuSplit[1]

    units = convert_units(units)
    
    ppu = cost +" / "+units
    return ppu

def convert_to_ounces(weight):
    if weight is None:
        return weight        
    ret = 0
    weight.replace(' ','')
    if (weight.find("ounce") != -1):
        ret = weight.replace('ounce','')
    else:
        print ("convert_to_ounces - unsupported weight of: " + weight)

    return ret

def clean_string(string,list_to_clean):
    for item in list_to_clean:
        string = string.replace(item,"")
    return string

class wegmansScraper(scrapy.Spider):
    name = "wegmans_spider"
    store_name = "wegmans"  
    start_urls = ['https://shop.wegmans.com/shop/categories','https://shop.wegmans.com/shop/categories/470']
    base_url = "https://shop.wegmans.com"
    section_dict = {}
    urls = []
    processedUrls = []
    conn = ""
    store_id=-1

    def get_next_url(self):
        sql=f"SELECT url from urlTable WHERE scraped=0 ORDER BY updated LIMIT 1"
        self.cursor.execute(sql)
        url=self.cursor.fetchone()
        return url

    def store_url(self,url,category,section,subsection):
        #TODO don't store duplicates
        # If entry in urls
        #increment hits
        time=datetime.datetime.now()
        store_url_sql = f"INSERT INTO urlTable (url, store, scraped, Updated, category, section, subsection) VALUES (\"{url}\",{self.store_id},0,\"{time}\",\"{category}\",\"{section}\",\"{subsection}\");"
        store_query=f"SELECT Hits FROM urlTable where url='{url}'"
        cursor = self.conn.cursor()
        cursor.execute(store_query)
        hits=cursor.fetchone()
        print (f"store_url_sql - {store_url_sql}")
        if hits is None:
            self.cursor.execute(store_url_sql)
            self.conn.commit()
        else:
            hits=hits[0]+1
            url_query=f"SELECT id FROM urlTable where url='{url}'"
            print(f"url_query - {url_query}")
            self.cursor.execute(url_query)
            fetched_id=self.cursor.fetchone()[0]
            update=f" UPDATE urlTable SET hits={hits} WHERE id={fetched_id}"
            print(f"url_query - {update}")
            self.cursor.execute(update)
            self.conn.commit()            

    def finish_url(self,url):
        url_query=f"SELECT id FROM urlTable where url='{url}'"
        self.cursor.execute(url_query)
        fetched_id=self.cursor.fetchone()

        url_update=f" UPDATE urlTable SET scraped=1 WHERE id={fetched_id}"
        self.cursor.execute(url_update)
        self.conn.commit()

        return fetched_id

    def start_requests(self):
        store_query=f"SELECT id FROM storeTable where name='{self.store_name}'"
        self.cursor = self.conn.cursor()
        self.cursor.execute(store_query)
        self.store_id=self.cursor.fetchone()[0]
        #self.store_id=clean_string(self.store_id,['(',')',','])

        #print (f"************** Fetched_id {fetched_id}")
        for url in self.start_urls:
            self.store_url(url,"","","")
            print(f"Starting requests with - {url}")
            yield SeleniumRequest(
                url=url,
                callback=self.parse_urls,
                wait_time=5,
                wait_until=EC.element_to_be_clickable((By.ID, 'nav-main-shop-category-1'))
            )

    def parse_urls(self, response):
        inspect_response(response,self)

        self.section_group = response.css(".subcategory.category")
        section_group = response.css(".subcategory.category")
        for section in section_group:
            section_name = section.css(".css-1pita2n ::text").get()
            url_nodes = section.css("ul.children a")
            for url_node in url_nodes:
                subsection_name = url_node.css("::text").get() 
                url = self.base_url + url_node.css("::attr(href)").get()
                self.section_dict[url] = (section_name, subsection_name)
                self.urls.append(url)                

        while len(self.urls) != 0:
                url = self.urls.pop()
                self.processedUrls.append(url)
                yield SeleniumRequest(
                    url=url,
                    callback=self.parse,
                    wait_time=5,
                    wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.full.cart.add'))
                )

    def parse(self, response):

        url=response.url
        items = response.css('.cell-content-wrapper')
        #check if it has a next button,
        next_page=response.css('[aria-label="Next"]').get()
        if next_page is not None:
            page_string="?page="
            page_str_len=len(page_string)
            i = url.find(page_string)
            #if yes, check url if it has a page part on it
            if i == -1:
            #if no, add ?page=2 to it
                next_url = url + page_string+"2"
            else:
            #if yes, extract page and add 1 
                page_number = i+page_string_len
                current_page = int(url[page_number:])
                next_page = current_page + 1
                next_url = url[:page_number] + str(next_page)
            print (f"Handling url - {next_url}")
            yield SeleniumRequest(
                    url=next_url,
                    callback=self.parse,
                    wait_time=5,
                    wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.full.cart.add'))
                )
            #inspect_response(response,self)
            #then add to self.urls
        
        for item in items:
            name=item.css('.cell-title-text ::text').get()
            price=item.css('[data-test="amount"] .css-19m8h51 ::text').get()
            price=convert_dollars(price)
            
            quantity=item.css('[data-test="amount"] .css-cpy6p ::text').get()

            ounces=item.css('.cell-product-size ::text').get()
            ounces=convert_to_ounces(ounces)

            ppu=item.css('[data-test="per-unit-price"] ::text').get()
            ppu=convert_ppu(ppu)
            section=self.section_dict[url][0]
            subsection=self.section_dict[url][1]

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

        #inspect_response(response,self)
