def lookup_category(section,subsection):
	category=""
	return category

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

