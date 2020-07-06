def lookup_category(name,section,subsection):
	categories = {
	           #"Category name" : "search terms"
               "pet"    : ["dog","cat","pet"],
               "baby"   : ["baby","diaper"],
               "pizza"  : ["pizza"],
               "dips"   : ["dip","queso","hummus","salsa"],
               "baked"  : ["bakery","bread","bagel","roll","muffin","donut"],
               "snacks" : ["snack","cookie","chip","pretzel","cand"],
               "seafood": ["seafood","fish","crab","lobster","clam","scallop","shrimp"],
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
        units = "EA"
    elif units == "fl. oz.":
        units = "FLOZ"
    elif units == "sq. ft.":
        units = "SQFT"
    elif units == "yd. ":
        units = "YD"
    return units

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


def parse_float(input_list):
    if input_list:
        f = float(input_list[0])
    else:
        f = 0
    return f

def read_script(script_file):
    file = open(script_file)
    script = file.read()
    file.close()
    return script

def convert_dollars(price):
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

