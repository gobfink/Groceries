#! /usr/local/bin/python3

import scrapy
from scrapy.shell import inspect_response
from util import convert_dollars, convert_units
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest


def convert_ppu(incoming_ppu):
    if not incoming_ppu:
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
    ret = 0
    weight.replace(' ','')
    if (weight.find("ounce") != -1):
        ret = weight.replace('ounce','')
    else:
        print ("convert_to_ounces - unsupported weight of: " + weight)

    return ret


class wegmansScraper(scrapy.Spider):
    name = "wegmans_spider"
    store_name = "wegmans"  
    start_urls = ['https://shop.wegmans.com/shop/categories','https://shop.wegmans.com/shop/categories/470']
    base_url = "https://shop.wegmans.com"
    section_dict = {}
    urls = []
    processedUrls = []

    def start_requests(self):
        for url in self.start_urls:
            print(f"Starting requests with - {url}")
            yield SeleniumRequest(
                url=url,
                callback=self.parse_urls,
                wait_time=20,
                wait_until=EC.element_to_be_clickable((By.ID, 'nav-main-shop-category-1'))
            )

    def parse_urls(self, response):
        self.section_group = response.css(".subcategory.category")
        section_group = response.css(".subcategory.category")
        for section in section_group:
            section_name = section.css(".css-1pita2n ::text").get()
            url_nodes = section.css("ul.children a")
            for url_node in url_nodes:
                subsection_name = url_node.css("::text").get() 
                url = self.base_url + url_node.css("::attr(href)").get()
                self.section_dict[url] = (section_name, subsection_name)                

        print ("section_dict - " + str(self.section_dict))
        for url in self.section_dict.keys():
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=20,
                wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.full.cart.add'))
            )
            #inspect_response(response,self)

    def parse(self, response):

        items = response.css('.cell-content-wrapper')
        for item in items:
            name=item.css('.cell-title-text ::text').get()
            price=item.css('[data-test="amount"] .css-19m8h51 ::text').get()
            price=convert_dollars(price)
            
            quantity=item.css('[data-test="amount"] .css-cpy6p ::text').get()

            ounces=item.css('.cell-product-size ::text').get()
            ounces=convert_to_ounces(ounces)

            ppu=item.css('[data-test="per-unit-price"] ::text').get()
            ppu=convert_ppu(ppu)
            url=response.url
            section=self.section_dict[url][0]
            subsection=self.section_dict[url][1]
            print(f"name - {name}, price - {price}, quantity - {quantity}, ounces - {ounces}, ppu - {ppu}, url - {url}, section - {section}, subsection - {subsection} ")
            inspect_response(response,self)
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
