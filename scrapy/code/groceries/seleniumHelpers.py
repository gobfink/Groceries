from scrapy_selenium import SeleniumRequest


# @description creates a parse request that isn't stopped by duplicate filters
# @param string url - url to request from
# @param function call_back - call back to point to once yielded
# @param selenium.EC(tuple) wait_until - Expected condition to wait for
# @param function errback - function to call on an error
# @param string meta_url - the meta url to check to see if the urls is valid
# @param boolean cookies - whether or not to use cookies (default true)
# @returns SeleniumRequest request - request created with above parameters
def create_unfiltered_parse_request(url, callback, wait_until, errback=None, meta_url="", cookies=True):
    if meta_url == "":
        meta_url = url
    request = create_parse_request(
        url, callback, wait_until, errback=errback, meta_url=meta_url, filter=False, cookies=cookies)
    return request


# @description creates a parse request
# @param string url - url to request from
# @param function call_back - call back to point to once yielded
# @param selenium.EC(tuple) wait_until - Expected condition to wait for
# @param string meta_url - the meta url to check to see if the urls is valid
# @param function errback - errorback function to hit when errorerd out
# @param boolean cookies=True - whether or not to use cookies
# @param boolean filter=True - whether or not to use the duplicate filter
# @param int attempt=1 - the attempt it has at scraping it
# @returns SeleniumRequest request - request created with above parameter
def create_parse_request(url, callback, wait_until, errback=None, meta_url="", cookies=True, filter=True, attempt=1):
    request = SeleniumRequest(
        url=url,
        callback=callback,
        wait_time=5,
        dont_filter=not filter,
        meta={'url': url, 'dont_merge_cookies': not cookies, 'attempt': attempt},
        errback=errback,
        wait_until=wait_until
    )
    return request
