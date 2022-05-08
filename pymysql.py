from flask import Flask
from  flaskext.mysql import  MySQL 

app = Flask(__name__)
mysql1 = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'jntuk'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



conn = mysql1.connect()

cursor = conn.cursor(mysql.pymysql.cursors.DictCursor)
		
sql = "SHOW TABLES"
		
cursor.execute(sql)
		
rows = cursor.fetchall()

for i in rows:
    print(i)

if __name__ == "__main__":
    app.run(debug=True)