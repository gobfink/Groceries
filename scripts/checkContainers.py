import docker

client=docker.from_env()
containers=client.containers.list()
names = []
for container in containers:
    names.append(container.name)

def lidlUp():
   lidlUrls='groceries_lidl-urls_1' in names
   lidlGroc='groceries_lidl-groceries_1' in names
   lidl='groceries_lidl_1' in names
   return(lidlUrls and lidlGroc and lidl)

def harrisUp():
   harrisUrls='groceries_harris-teeter-urls_1' in names
   harris='groceries_harris-teeter_1' in names
   return(harrisUrls and harris)

def safewayUp():
   safewayUrls='groceries_safeway-urls_1' in names
   safewayGroc='groceries_safeway-groceries_1' in names
   safeway='groceries_safeway_1' in names
   return(safewayUrls and safewayGroc and safeway)

def wegmansUp():
   return('groceries_wegmans_1' in names)

def walmartUp():
   return('groceries_walmart_1' in names)

def flaskUp():
   retval='groceries_flask_1' in names
   return(retval)

def adminerUp():
   retval='groceries_splash-middleware_1' in names
   return(retval)

def middleUp():
   retval='groceries_adminer_1' in names
   return(retval)

def dbUp():
   retval='groceries_db_1' in names
   return(retval)

def coreUp():
   return(flaskUp() and adminerUp() and middleUp() and dbUp())

def printStats(status):
   #print(status)
   print("\tDocker Status\n\t===============\n\tCore:\t\t%s\n\tWegmans:\t%s\n\tSafeway:\t%s\n\tLidl:\t\t%s\n\tWalmart:\t%s\n\tHarris Teeter:\t%s\n"%(status[0],status[1],status[2],status[3],status[4],status[5]))
   return

status=(coreUp(),wegmansUp(),safewayUp(),lidlUp(),walmartUp(),harrisUp())
printStats(status)
