import datetime
import MySQLdb



def lookup_category(name,section,subsection):
	categories = {
	           #"Category name" : "search terms"
               "pet"    : ["dog","cat","pet"],
               "baby"   : ["baby","diaper"],
               "pizza"  : ["pizza"],
               "dips"   : ["dip","queso","hummus","salsa"],
               "seafood": ["seafood","fish","crab","lobster","clam","scallop","shrimp","sushi"],
               "baked"  : ["bakery","bread","bagel","roll","muffin","donut"],
               "snacks" : ["snack","cookie","chip","pretzel","cand"],
               "meat"   : ["meat","beef","steak","bacon","sausage","chicken","pork","meat"],
               "pasta"  : ["pasta"],
               "dessert": ["dessert","pie","ice cream","frozen yogurt", "cake"],
               "juice"  : ["juice"],
               "oil"    : ["oil"],
               "alcohol": ["alcohol","wine","beer","rum","vodka","liquer"],
               "cheese" : ["cheese"],
               "fruit"  : ["fruit","orange","banana","apple","peach"],
               "produce": ["vegetable","fresh","corn","tomato","onion","potato","produce"],
	}
	name=name.lower()
	section=section.lower()
	subsection=subsection.lower()
	ret=""
	for category,terms in categories.items():
		if any(term in subsection for term in terms):
			ret=category
			break
		elif any(term in section for term in terms):
			ret=category
			break
		elif any(term in name for term in terms):
			ret=category
			break
		
	return ret

def convert_units(units):
    if units == "ounce":
        units = "OZ"
    elif units == "lb.":
        units = "LB"
    elif units == "each":
        units = "EA"
    elif units == "ct.":
        units = "CT"
    elif units == "fl. oz.":
        units = "FLOZ"
    elif units == "sq. ft.":
        units = "SQFT"
    elif units == "yd. ":
        units = "YD"
    return units

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
    elif (weight.find("lb.") != -1):
        ret = weight.replace('lb.','')
        ret = float(ret) * 16
    else:
        print ("convert_to_ounces - unsupported weight of: " + weight)

    return ret

def convert_dollars(price):
    if price is None:
      return 0
    p = price
    p = p.replace('$','')
    return p

def convert_cents(price):
    p = price
    if price.find('¢') is not -1:
        p = p.replace('¢','')
        p = p.replace('.','')
        p = "0." + p
    return p

def handle_none(arg):
    if arg is None:
        return 0
    else:
        return arg

def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script


def parse_float(float_in):
    try:
        f = float(float_in)
    except ValueError:
        print (f"Parse_float - {float_in} is not a float")
        f = 0 
    return f

def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script

def clean_string(string,list_to_clean):
    for item in list_to_clean:
        string = string.replace(item,"")
    return string
def get_url_metadata(cursor,url):
        sql=f"SELECT category, section, subsection FROM urlTable WHERE url=\"{url}\""
        print(f'get_url_metadata - {sql}')
        cursor.execute(sql)
        metadata=cursor.fetchone()
        return (metadata)

def get_next_url(cursor,iteration):
    sql=f"SELECT url from urlTable WHERE scraped=0 ORDER BY updated DESC LIMIT {iteration}"
    cursor.execute(sql)
    url=cursor.fetchone()
    if url is None:
        print ("get_next_url | couldn't find anymore urls to get returning none")
    else:
        url=url[0]
    return url

def store_url(conn,url,store_id,category,section,subsection):
    time=datetime.datetime.now()
    #url=url.replace("\'","\'\'")
    store_query=f"SELECT Hits FROM urlTable where url=\"{url}\" AND store_id='{store_id}'"
    print (f"store_query - {store_query}")
    cursor = conn.cursor()
    cursor.execute(store_query)
    hits=cursor.fetchone()
    if hits is None:
        store_url_sql = f"INSERT INTO urlTable (url, store_id, scraped, Updated, category, section, subsection, hits) VALUES (\"{url}\",{store_id},0,\"{time}\",\"{category}\",\"{section}\",\"{subsection}\",1);"
        print (f"store_url_sql - {store_url_sql}")
        cursor.execute(store_url_sql)
        conn.commit()
    else:
        hits=hits[0]+1
        update=f" UPDATE urlTable SET hits={hits} WHERE url=\"{url}\" AND store_id='{store_id}'"
        print(f"update - {update}")
        cursor.execute(update)
        conn.commit()

def finish_url(conn,store_id,url):
    url_update=f" UPDATE urlTable SET scraped=1 WHERE url=\"{url}\" AND store_id='{store_id}'"
    cursor=conn.cursor()
    print(f"finish_url - {url_update}")
    cursor.execute(url_update)
    conn.commit()
    return url

def find_store_id(cursor, store_name, location):
    store_query=f"SELECT id FROM storeTable where name='{store_name}' AND location='{location}'"
    cursor.execute(store_query)
    store_id=cursor.fetchone()[0]
    return store_id

def update_location_db(conn,location,store_id):
    cursor=conn.cursor()
    store_update=f"UPDATE storeTable SET location=\"{location}\" WHERE id=\"{store_id}\""
    cursor.execute(store_update)
    conn.commit()