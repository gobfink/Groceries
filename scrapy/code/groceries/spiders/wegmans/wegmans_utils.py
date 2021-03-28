#! /usr/local/bin/python3

#import scrapy
import time

def close_modal(spider):
    close_button = spider.driver.find_elements_by_css_selector(
        '#shopping-selector-parent-process-modal-close-click')
    if close_button:
        spider.logger.info("Closing modal")
        close_button[0].click()
        time.sleep(.5)
    else:
        spider.logger.info("No Modal detected continuing")
def change_store_location(spider):
    store_button = spider.driver.find_element_by_css_selector(
        '[data-test="store-button"]')
    current_store = store_button.text
    if current_store == spider.location:
        spider.logger.info(
            f"Current location = {current_store} is correct. Continuing.")
        return
    store_button.click()
    time.sleep(spider.delay)
    stores = spider.driver.find_elements_by_css_selector('.store-row')
    # Go through each of the stores, until one matches the text, then click on it
    for store in stores:
        name = store.find_element_by_css_selector('.name')
        store_name = name.text
        #print (f"change_store_location - {name.text}")
        if store_name == spider.location:
            button = store.find_element_by_css_selector(
                '[data-test="select-store-button"]')
            button.click()
            time.sleep(spider.delay)
            spider.logger.info(f"Set location to {store_name}")
            return
    spider.logger.warn(f"Could not set location to {self.location}")
