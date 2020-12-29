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
