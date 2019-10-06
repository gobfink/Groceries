from urls import get_top_urls
import requests, os, time

cwd = os.getcwd()
webdata = cwd + "/webdata"


top_urls=get_top_urls()
print (top_urls)
timestamp = time.time()

for key in top_urls:
	# Create a data directory to store the webpage
	data_path=webdata+"/"+str(timestamp)+"/"+key 
	if (not os.path.exists(data_path)):
		print("Creating Webdata directory: "+data_path)
		os.makedirs(data_path)
	else:
		print ("Webdata directory already exists at: " +data_path)
	# Pull down the webpage
	url = (top_urls[key])
	page = requests.get(url)
	name = url.replace("https://","")

	#we will have to save the webpage ourselves
	with open(data_path+"/"+name, 'w') as file:
		file.write(page.text)