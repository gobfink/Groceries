# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import datetime
import time

from scrapy.exceptions import NotConfigured

from util import handle_none,lookup_category

class GroceriesPipeline(object):

        def __init__(self, db, user, passwd, host):
                self.db = db
                self.user = user
                self.passwd = passwd
                self.host = host

        @classmethod
        def from_crawler(cls, crawler):
                db_settings = crawler.settings.getdict('DB_SETTINGS')
                if not db_settings:
                        raise NotConfigured
                db = db_settings['db']
                user = db_settings['user']
                passwd = db_settings['passwd']
                host = db_settings['host']

                return cls(db, user, passwd, host)

        def open_spider(self, spider):
                self.store_name = spider.store_name
                self.location = handle_none(spider.location)
                self.date = datetime.datetime.now()
                self.conn = MySQLdb.connect(db=self.db,
                                              user=self.user,
                                              passwd=self.passwd,
                                              host=self.host,
                                              charset='utf8', use_unicode=True)
                spider.conn = self.conn
                #Look for the store in the store_table
                store_query=f"SELECT id FROM storeTable where name='{self.store_name}' AND location='{self.location}'"
                self.cursor = self.conn.cursor()
                spider.cursor = self.cursor
                self.cursor.execute(store_query)
                fetched_id=self.cursor.fetchone()
                #if it doesn't exist then add it
                if fetched_id is None:
                    #TODO it would be nice to query the actually set location instead of trusting it to get set correctly
                    add_store = f"INSERT INTO storeTable (name, location) VALUES (\"{self.store_name}\", \"{self.location}\");"
                    print(add_store)
                    self.cursor.execute(add_store)
                    self.conn.commit()
                    time.sleep(.5)

                    self.cursor.execute(store_query)
                    fetched_id=self.cursor.fetchone()

                self.store_id=fetched_id[0]

        def process_item(self, item, spider):
        # sql = "INSERT INTO table (field1, field2, field3) VALUES (%s, %s, %s)"
        # TODO update the ids into the other values appropriately
            name = item.get("name")
            price = float(handle_none(item.get("price")))
            section = handle_none(item.get("section"))
            subsection = handle_none(item.get("subsection"))
            category = lookup_category(name,section,subsection)
            print (f"process_item - {name} with category - {category}")
            ounces = handle_none(item.get("ounces"))
            unit = handle_none(item.get("unit"))

            reported_price_per_unit = handle_none(item.get("price-per-unit"))
            brand = ""
            date = self.date
            store_id = self.store_id
            url = item.get("url")
            #TODO break this into multiple lines
            sql = f" INSERT INTO groceryTable (name, category, section, subsection, price, unit, ounces, reported_price_per_unit, brand, date, store_id, url) VALUES (\"{name}\",\"{category}\",\"{section}\",\"{subsection}\",{price},'{unit}',{ounces},\"{reported_price_per_unit}\",\"{brand}\",\"{date}\",{store_id},\" {url} \");"

            #print ( "adding sql : "+ sql )
            self.cursor.execute(sql)
            self.conn.commit()
            return item

        def close_spider(self, spider):
            self.conn.close()

