from flask import Flask, render_template
#from flask_sqlalchemy import SQLAlchemy
from dbconn import connection


#db = SQLAlchemy()
app = Flask(__name__)
#db.init_app(app)

@app.route('/')
def home():
   return "<h1>Got Here!</h1>"


@app.route('/dashboard/')
def dashboard():
   try:
     c, conn = connection()
     return("okay")
   except Exception as e:
     return(str(e))
   query = "SELECT * from tbl_User"
   c.execute(query)
   data = c.fetchall()
   conn.close()

   return render_template("dashboard.html",data=data)


if __name__ == "__main__":
   app.run(host='0.0.0.0',port=80)
