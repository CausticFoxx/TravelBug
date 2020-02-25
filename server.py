from flask import Flask, render_template, request, redirect
from datetime import datetime

# a cursor is the object we use to interact with the database
import pymysql.cursors
# this class will give us an instance of a connection to our database
class MySQLConnection:
    def __init__(self, db):
        connection = pymysql.connect(host = 'localhost',
                                    user = 'root', # change the user and password as needed
                                    password = 'root', 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        # establish the connection to the database
        self.connection = connection
    # the method to query the database
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                print("Running Query:", query)
     
                executable = cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    # INSERT queries will return the ID NUMBER of the row inserted
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                    result = cursor.fetchall()
                    return result
                else:
                    # UPDATE and DELETE queries will return nothing
                    self.connection.commit()
            except Exception as e:
                # if the query fails the method will return FALSE
                print("Something went wrong", e)
                return False
            finally:
                # close the connection
                self.connection.close() 
# connectToMySQL receives the database we're using and uses it to create an instance of MySQLConnection
def connectToMySQL(db):
    return MySQLConnection(db)

app = Flask(__name__)

@app.route("/")
def index():
  mysql = connectToMySQL("users")
  users = mysql.query_db("SELECT * FROM users;")
  print(users)
  return render_template("index.html", users = users)

@app.route("/users")
def users():
  print(request.form)
  mysql = connectToMySQL("users")
  users = mysql.query_db("SELECT * FROM users;")
  return render_template("users.html",users = users)

@app.route("/users/new")
def new():
  print(request.form)
  mysql = connectToMySQL("users")
  users = mysql.query_db("SELECT * FROM users;")
  return render_template("new.html",users = users)


@app.route("/add_user", methods=["POST"])
def add_friend_to_db():
  print(request.form)
  mysql = connectToMySQL("users")
  # id = len(mysql.query_db("select id from users"))+1
  id = 1
  print(id)
  query = "INSERT INTO users (id, first_name, last_name, email, created_at, updated_at) VALUES (%(id)s, %(fn)s, %(ln)s, %(email)s, NOW(), NOW());"

  data = {
    "id": id,
    "fn": request.form["fn"],
    "ln": request.form["ln"],
    "email": request.form["email"],
    "created_at": datetime.now(),
    "updated_at": datetime.now()
  }
  new_user = mysql.query_db(query,data)
  return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)