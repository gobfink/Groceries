import datetime
import MySQLdb
import re

# @description returns the category based on the name, section, and subsection
# @param string name - name to return the category for
# @param string section - section used to determine the category
# @param string subsection - subsection used to determine the category
# @param string ret - the category determined from the name, section, and subsection
def lookup_category(name, section, subsection):
    categories = {
        #"Category name" : "search terms"
        "pet": ["dog", "cat", "pet"],
        "baby": ["baby", "diaper"],
        "pizza": ["pizza"],
        "dips": ["dip", "queso", "hummus", "salsa"],
        "seafood": [
            "seafood", "fish", "crab", "lobster", "clam", "scallop", "shrimp",
            "sushi"
        ],
        "baked": ["bakery", "bread", "bagel", "roll", "muffin", "donut"],
        "snacks": ["snack", "cookie", "chip", "pretzel", "cand"],
        "meat": [
            "meat", "beef", "steak", "bacon", "sausage", "chicken", "pork",
            "hotdog", "hot dog"
        ],
        "pasta": ["pasta"],
        "dessert": ["dessert", "pie", "ice cream", "frozen yogurt", "cake"],
        "juice": ["juice"],
        "oil": ["oil"],
        "alcohol": ["alcohol", "wine", "beer", "rum", "vodka", "liquer"],
        "cheese": ["cheese"],
        "fruit": ["fruit", "orange", "banana", "apple", "peach"],
        "produce":
        ["vegetable", "corn", "tomato", "onion", "potato", "produce"],
        "dairy" : ["dairy"],
    }

    exclusions = {
        "pet": ["hotdog", "hot dog", "categories", "petite"],
        "baby": ["ribs"],
        "oil": ["foil", "free"],
        "alcohol": ["vinegar", "root", "non"],
        "seafood": ["scalloped"],
    }

    name = name.lower()
    section = section.lower()
    subsection = subsection.lower()
    ret = ""
    for category, terms in categories.items():
        if category in exclusions:
            exclusion = exclusions[category]
        else:
            exclusion = []
        sections_and_name=subsection+" "+section+" "+name

        if any(excl in sections_and_name for excl in exclusion):
            #print(f" excluding - {sections_and_name} because of exclusion found in - {exclusion} for category {category}")
            continue
        elif any(term in sections_and_name for term in terms):
            #print(f" found and matched- {sections_and_name} with terms - {terms} for category {category}")
            ret = category
            break
    return ret



# @description converts the price per unit to something generic that can be compared
# @param string - incoming_ppu used to derive the ppu from
# @returns string - ppu that can be used to compare between different stores
def convert_ppu(incoming_ppu):
    if incoming_ppu is None:
        return ""
    ppu = incoming_ppu
    charactersToRemove = ['$', '(', ')']
    for remove in charactersToRemove:
        ppu = ppu.replace(remove, '')
    ppuSplit = ppu.split('/')
    cost = ppuSplit[0]

    units = ppuSplit[1]

    units = convert_units(units)

    ppu = cost + " / " + units
    return ppu


# @description converts the weigh to ounces
# @param weight - weight to convert to ounces
# @returns float ret - ounces derived from the weight, or 0 if ounces couldn't be derived
def convert_to_ounces(weight):
    if weight is None:
        return 0
    ret = 0
    weight = str(weight)
    weight.replace(' ', '')
    weight=weight.lower()
    quantity = 1
    if (weight.find("-") != -1):
        try:
            quantity = re.findall("([0-9]+)-",weight)[0]
            weight = re.findall("-([0-9]*.[0-9]*)",weight)[0]
        except IndexError:
            print(f"Could not find parse a weight from: {weight}")
            quantity = 0
            weight = 0
    try:
        weight = str(weight)
        if (weight.find("fl") != -1):
            #can't convert fluid ounces to regular ounces
            ret = 0
        elif (weight.find("ounce") != -1):
            ret = float(weight.replace('ounce', ''))
        elif (weight.find("oz.") != -1):
            ret = float(weight.replace("oz.",''))
        elif (weight.find("oz") != -1):
            ret = float(weight.replace("oz",''))
        elif (weight.find("lb.") != -1):
            ret = weight.replace('lb.', '')
            ret = float(ret) * 16
        elif (weight.find("lbs.") != -1):
            ret = weight.replace('lbs.','')
            if ret.isdigit():
                ret = float(ret) * 16
            else:
                print(f"convert_to_ounces - {ret} - is not a digit")
                ret = 0
        else:
            print("convert_to_ounces - unsupported weight of: " + weight)
    except ValueError:
        print(f"Couldn't convert weight: {weight}, to ounces returning 0")
        ret = 0
    return ret * quantity

# @decription - removes $ from price
# @param string price - string of the form $XX.XX to XX.XX
# @returns string p - price without $ or 0 if None
def convert_dollars(price):
    if price is None:
        return 0
    p = price
    p = p.replace('$', '')
    return p

# @description - converts cents to dollars
# @param string price to convert to dollars
# @returns string price in dollars
def convert_cents(price):
    p = price
    if price.find('¢') != -1:
        p = p.replace('¢', '')
        p = p.replace('.', '')
        p = "0." + p
    return p

# @description checks if arg is None and replaces with 0 if it is
# @param string or None arg to be handled the None condition
# @returns 0 if it was None else the same argument
def handle_none(arg):
    if arg is None:
        return 0
    else:
        return arg

# @description reads a file into a string
# @param string script_file - location to read
# @returns string script - contents of the script to read
def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script

# @description checks if float_in can be a float
# @param string float_in - to be checked if it can be a float
# @returns float f - 0 if it raised a ValueError else float(float_in)
def parse_float(float_in):
    try:
        f = float(float_in)
    except ValueError:
        print(f"Parse_float - {float_in} is not a float")
        f = 0
    return f

# @description removes list_to_clean from string
# @param string string - string to be cleaned
# @param list[strings] list_to_clean - list to remove from string
# @returns string string - string without any strings in list_to_clean
def clean_string(string, list_to_clean):
    for item in list_to_clean:
        string = string.replace(item, "")
    return string

# @description gets the category, section, subsection assocataited withh the url
# @param MySQLDb.cursor - cursor used to fetch the data from the connection
# @param string url - url to get metadata from
# @returns (string,string,string) - category,section,subsection found in urlTable for url
def get_url_metadata(cursor, url):
    sql = f"SELECT category, section, subsection FROM urlTable WHERE url=\"{url}\""
    print(f'get_url_metadata - {sql}')
    cursor.execute(sql)
    metadata = cursor.fetchone()
    return (metadata)

# @description gets the next url in the database offset by iteration
# @param MySQLDb.cursor - cursor used to fetch the data from the connection
# @param int iteration - iteration used to offset from the table
# @param int store_id - store_id to filter for when looking for urls, -1 will use all
# @param Boolean scrape_urls - if set to true, this will look for the scraped_urls flag instead
# @param string filter - filters the url for the given string
# @returns string url - next url found in the database pointed to by cursor
def get_next_url(cursor, iteration, store_id=-1,scrape_urls=False,filter=""):
    sql = f"SELECT url from urlTable WHERE Scraped=0 ORDER BY updated DESC LIMIT {iteration}"
    #if store_id == -1:
    #    sql = f"SELECT url from urlTable WHERE Scraped=0 ORDER BY updated DESC LIMIT {iteration}"
    #else:
    #    sql = f"SELECT url from urlTable WHERE Scraped=0 AND store_id={store_id} ORDER BY updated DESC LIMIT {iteration}"
    if filter != "":
        sql = sql.replace("ORDER", f"AND Url LIKE '%{filter}%' ORDER")
    if store_id != -1:
        sql = sql.replace("WHERE", f"WHERE store_id={store_id} AND")
    if scrape_urls:
        sql = sql.replace("Scraped","Scraped_Urls")

    print (f"Running - {sql}")
    cursor.execute(sql)
    url = cursor.fetchone()
    if url is None:
        print(
            "get_next_url | couldn't find anymore urls to get returning none")
    else:
        url = url[0]
    return url

# @description stores the url for the associated store_id, category, section, and subsection
# @param MySQLDb.conn - connection to the database
# @param string url - url to store in the database
# @param int store_id - id of the store refered to
# @param string category - category of the store the url refers to
# @param string section - section of the store the url refers to
# @param string subsection - subsection of the store the url refers to
# @param int grocery_quantity - number of groceries to expect for this url's subsection
def store_url(conn, url, store_id, category, section, subsection, grocery_quantity=0):
    time = datetime.datetime.now()
    #url=url.replace("\'","\'\'")
    store_query = f"SELECT Hits FROM urlTable where url=\"{url}\" AND store_id='{store_id}'"
    print(f"store_query - {store_query}")
    cursor = conn.cursor()
    cursor.execute(store_query)
    hits = cursor.fetchone()
    if hits is None:
        store_url_sql = ("INSERT INTO urlTable (url, store_id, scraped, scraped_urls, Updated, category, section, subsection, hits, grocery_quantity)"
                         f" VALUES (\"{url}\",{store_id}, 0, 0,\"{time}\",\"{category}\",\"{section}\",\"{subsection}\",1,{grocery_quantity});")
        print(f"store_url_sql - {store_url_sql}")
        cursor.execute(store_url_sql)
        conn.commit()
    else:
        hits = hits[0] + 1
        update = f" UPDATE urlTable SET hits={hits} WHERE url=\"{url}\" AND store_id='{store_id}'"
        print(f"update - {update}")
        cursor.execute(update)
        conn.commit()


# @description sets scraped=1 for url
# @param MySQLDb.connection - connection used to fetch/store the data from the database
# @param int store_id - store_id associated with the url to update
# @param string url - url to update
# @param bool scrape_urls - sets scraped_urls instead of scraped for the url
# @returns string url - url updated
def finish_url(conn, store_id, url,scrape_urls=False):
    url_update = f" UPDATE urlTable SET scraped=1 WHERE url=\"{url}\" AND store_id='{store_id}'"
    if scrape_urls:
        url_update = url_update.replace("scraped","scraped_urls")
    cursor = conn.cursor()
    print(f"finish_url - {url_update}")
    cursor.execute(url_update)
    conn.commit()
    return url

# @description finds the corresponding store_id for store_name and location
# @param MySQLDb.cursor - cursor used to fetch the data from the connection
# @param string store_name - store_name used to find the store_id for
# @param string location - address of the store to find the store_id for
# @returns int store_id
def find_store_id(cursor, store_name, location):
    store_query = f"SELECT id FROM storeTable where name='{store_name}' AND location='{location}'"
    cursor.execute(store_query)
    store_id = cursor.fetchone()[0]
    return store_id

# @description determines if the section is in the store_id
# @param MySQLDb.cursor - cursor used to fetch the data from the connection
# @param int store_id store_id to look in
# @param string section the section to look for inside of the store_id
# @returns true if it finds a match else false
def is_section_in_store_id(cursor, store_id, section):
    section_query = f"SELECT * FROM urlTable where store_id='{store_id}' AND section='{section}' AND subsection=''"
    cursor.execute(section_query)
    ret = cursor.fetchone() is not None
    return ret

# @description determines if the subsection is in the store_id - excludes any Urls with the string pageNo
# @param MySQLDb.cursor - cursor used to fetch the data from the connection
# @param int store_id store_id to look in
# @param string section the section to look for inside of the store_id
# @param string subsection the subsection to look for inside of the store_id
# @param string urlExclusion a string to filter out of the urls when querying the database
# @returns true if it finds a match else false
def is_subsection_in_store_id(cursor, store_id, section, subsection, urlExclusion = ""):
    # Exclude the  `pageNo` string in case it was interrupeted in the middle of a crawling the pages for a section (the url without pageNo is added after)
    section_query = f"SELECT * FROM `urlTable` where `store_id` = \"{store_id}\" AND `Section` = \"{section}\" AND `Subsection`=\"{subsection}\" AND `Url` NOT LIKE \"%pageNo%\""
    print(f"is_subsection_in_store_id - section_query: {section_query}")
    cursor.execute(section_query)
    ret = cursor.fetchone() is not None
    return ret

# @description updates the location for a given store_id
# @param MySQLDb.connection - connection used to fetch/store the data from the database
# @param string location - address of the store to find the store_id for
# @param int store_id - store_id of the store to update the location for
def update_location_db(conn, location, store_id):
    cursor = conn.cursor()
    store_update = f"UPDATE storeTable SET location=\"{location}\" WHERE id=\"{store_id}\""
    cursor.execute(store_update)
    conn.commit()

# @description This function determines if the page supports pagination
# @Params string page_string - the string that is added to the url for the next page
# @Params string url - the url for the current page
# @returns string url of the next page or None if it doesn't support it
def get_next_pagination(page_string, url):
    page_str_len = len(page_string)
    i = url.find(page_string)
    #if yes, check url if it has a page part on it
    if i == -1:
        #if no, add page 2  to it
        next_page_url = url + page_string + "2"
    else:
        #if yes, extract page and add 1
        page_number = i + page_str_len
        current_page = int(url[page_number:])
        next_page = current_page + 1
        next_page_url = url[:page_number] + str(next_page)
    return next_page_url

# @description converts the units into a generic set of units used between spiders
# @Params string units - units to be converted and made generic
# @returns string units generified units
def convert_units(units):
    units=units.lower()
    units = clean_string(units,['.',' '])
    print (f"convert_units - {units}")
    if units == "ounce" or units == "oz":
        units = "OZ"
    elif units == "lb" or units == "lbs":
        units = "LB"
    elif units == "each" or units == "ea":
        units = "EA"
    elif units == "count" or units == "ct":
        units = "CT"
    elif units == "floz":
        units = "FLOZ"
    elif units == "sqft":
        units = "SQFT"
    elif units == "yd":
        units = "YD"
    elif units == "l":
        units = "L"
    elif units == "ml":
        units = "ML"
    return units

# @description trimgs a string from the end
# @param string trim_from - string to trim from
# @param string_to_trim - string to remove
# @returns string - trimmed string
def trim_url(trim_from,string_to_trim):
    if trim_from.endswith(string_to_trim):
        trim_from = trim_from.replace(string_to_trim,'')
    return trim_from


# @description checks the amount of groceries in the database for a given url
# @param MySQLDb.cursor - cursor used to fetch the data from the database
# @param string url - url to check
# @returns dictionary (bool finished, int expected,int found) - finished is if all subsections have been scraped,
#                                                          expected is the amount to be found for the given url,
#                                                          found is the amount found
def check_subsection_amount(cursor, url):
    ret = {
     "Finished": False,
     "Expected": 0,
     "Found": 0,
     "Url": url,
     "Subsection": ""
    }
    #SELECT `Subsection`, `Id` FROM `urlTable` WHERE `Url` = 'https://www.harristeeter.com/shop/store/313/category/0/subCategory/1003/products?isSpecialSubCategory=true' LIMIT 50
    quantitySql = f"SELECT (`grocery_quantity`) FROM `urlTable` WHERE `Url` = \"{url}\""
    #print(f"quantitySql: {quantitySql}")
    cursor.execute(quantitySql)
    quantity = cursor.fetchone()[0]
    print (f"found quantity: {quantity} from {quantitySql}")
    subsectionSql = f"SELECT `Subsection` FROM `urlTable` WHERE `Url` = \"{url}\""
    #print(f"subsectionSql: {subsectionSql}")
    cursor.execute(subsectionSql)
    subsection = cursor.fetchone()[0]
    print (f"found subsection: {subsection} from {subsectionSql}")

    finishedSql = f"SELECT MIN(`Scraped`) FROM `urlTable` WHERE `Subsection` = \"{subsection}\""
    cursor.execute(finishedSql)
    finished = cursor.fetchone()[0] == 1
    print (f"Finished: {finished} from {finishedSql}")

    countSql = f"SELECT COUNT(*) FROM `groceryTable` WHERE `subsection` = \"{subsection}\""
    cursor.execute(countSql)
    found = cursor.fetchone()[0]
    ret["Subsection"] = subsection
    ret["Finished"] = finished
    ret["Expected"] = quantity
    ret["Found"] = found

    print(f"ret - {ret}")
    print(f"For url - {url}: Expected={quantity}, Found={found}")

    return ret
