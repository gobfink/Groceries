import json
import base64
import scrapy
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response


def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script

class MySpider(scrapy.Spider):
    name ="lua_example"
    # ...
    def start_requests(self):
        url="https://grocery.walmart.com"
        script = """
        function main(splash)
            assert(splash:go(splash.args.url))
            assert(splash:wait(0.5))
            return splash:evaljs("document.title")
        end
        """
        script2 = """
        function main(splash, args)
            splash:go(splash.args.url)
            splash:wait(0.5)
            local title = splash:evaljs("document.title")
            return {title=title}
        end
        """
        script = read_script("buttonClick.lua")
        yield SplashRequest(url, self.parse_result, endpoint='execute', args={'lua_source': script})
    # ...
    def parse_result(self, response):
        html = response.body_as_unicode()
        file = open("lua_example.html","w")
        n = file.write(html)
        file.close()
        #doc_title = response.title()
        yield {
            'html' : html,
        }
    # ...