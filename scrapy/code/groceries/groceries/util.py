def lookup_category(name,section,subsection):
	categories = {
	           #"Category name" : "search terms"
               "baby"   : ["baby","diaper"],
               "pet"    : ["dog","cat","pet"],
               "pizza"  : ["pizza"],
               "dips"   : ["queso","hummus","salsa"],
               "cheese" : ["cheese"],
               "baked"  : ["bread","bagel","roll"],
               "snacks" : ["cookie","chip","pretzel","cand"],
               "seafood": ["seafood","fish","crab","lobster","clam","scallop","shrimp"],
               "meat"   : ["beef","steak","bacon","sausage","chicken","pork","meat"],
               "pasta"  : ["pasta"],
               "oil"    : ["oil"],
               "juice"  : ["juice"]
	}
	ret=""
	for category,terms in categories.items():
		if any(term in name for term in terms):
			ret=category
			break
		if any(term in subsection for term in terms):
			ret=category
			break
		if any(term in section for term in terms):
			ret=category
			break
		
	return ret

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

def convert_cents(price):
    p = price
    if price.find('¢') is not -1:
        p = p.replace('¢','')
        p = p.replace('.','')
        p = "0." + p
    return p

