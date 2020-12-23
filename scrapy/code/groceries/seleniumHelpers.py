from scrapy_selenium import SeleniumRequest


# @description creates a parse request that isn't stopped by duplicate filters
# @param string url - url to request from
# @param function call_back - call back to point to once yielded
# @param selenium.EC(tuple) wait_until - Expected condition to wait for
# @param string meta_url - the meta url to check to see if the urls is valid
# @returns SeleniumRequest request - request created with above parameters
def create_unfiltered_parse_request(url,callback,wait_until,meta_url=""):
    if meta_url == "" :
        meta_url = url
    request = SeleniumRequest(
                url=url,
                callback=callback,
                dont_filter=True,
                wait_time=5,
                meta={'url':meta_url},
                wait_until=wait_until
    			)
    return request


# @description creates a parse request
# @param string url - url to request from
# @param function call_back - call back to point to once yielded
# @param selenium.EC(tuple) wait_until - Expected condition to wait for
# @param string meta_url - the meta url to check to see if the urls is valid
# @returns SeleniumRequest request - request created with above parameters
def create_parse_request(url,callback,wait_until, meta_url=""):
    request = SeleniumRequest(
                url=url,
                callback=callback,
                wait_time=5,
                meta={'url':url},
                wait_until=wait_until
    			)
    return request
