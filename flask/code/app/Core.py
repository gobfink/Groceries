from . import db

def executeSQLm(sql):
    """
    """
    #with db.connect() as con:
    #    rs = con.execute(sql)
    rs=db.engine.execute(sql)
    return(rs)

def executeSQLr(sql):
    """
    """
    #with db.connect() as con:
    #    rs = con.execute(sql)
    rs=db.engine.execute(sql)
    return(rs.fetchone())

def executeSQL(sql):
    junk=executeSQLm(sql)
    return

def convRec(inrec):
    retval=[]
    for rec in inrec:
        retval.append(rec[0])
    return(retval)

def getStoreID(storename):
    sql = 'select id from storeTable WHERE name = \'' + storename + '\''
    print('getstore sql ' + sql)
    retval=executeSQLr(sql)
    return(retval)

def getStores():
    # Get store names for the store pick list
    sql = 'select distinct st.name, st.id from groceryTable as gt '
    sql+='left join storeTable as st on gt.store_id = st.id '
    sql+='order by st.name'
    retval=executeSQLm(sql)
#    return(convRec(retval))
    return(retval)

def getSections():
    # Get section names for the section pick list
    sql='select distinct section from groceryTable order by section'
    retval=executeSQLm(sql)
    return(convRec(retval))

def getSubSections():
    # Get subsection names for the subsection pick list
    sql='select distinct subsection from groceryTable order by subsection'
    retval=executeSQLm(sql)
    return(convRec(retval))
