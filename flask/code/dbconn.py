import MySQLdb

def connection():
    conn = MySQLdb.connect(host="db",
                           user="root",
                           passwd="example",
                           db="groceries")
    c = conn.cursor()
    return c, conn
