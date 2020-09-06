from scrapy_selenium import SeleniumRequest

def create_unfiltered_parse_request(url,callback,wait_until):
    request = SeleniumRequest(
                url=url,
                callback=callback, 
                dont_filter=True,
                wait_time=5, 
                wait_until=wait_until
    			)          
    return request

def create_parse_request(url,callback,wait_until):
    request = SeleniumRequest(
                url=url,
                callback=callback, 
                wait_time=5, 
                wait_until=wait_until
    			)          
    return request