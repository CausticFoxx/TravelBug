import re
from datetime import datetime

import pymysql.cursors
from flask import Flask, redirect, render_template, request


# this class will give us an instance of a connection to our database
class MySQLConnection:
    def __init__(self, db):
        connection = pymysql.connect(
            host='localhost',
            user='root',  # change the user and password as needed
            password='root',
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)
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


# Validator will validate inputs in forms
class Validator:
    def check_pw(
        self,
        password="",
        confirm_pw=""):  # password and confirm_pw values from request.form
        flag = False
        while True:
            if (len(password) < 8):
                flag = True
                return flag
            elif password != confirm_pw:
                flag = True
                return flag
            elif not re.search("[a-z]", password):
                flag = True
                return flag
            elif not re.search("[A-Z]", password):
                flag = True
                return flag
            elif not re.search("[0-9]", password):
                flag = True
                return flag
            elif not re.search("[_@$]", password):
                flag = True
                return flag
            elif re.search("\s", password):
                flag = True
                return flag
            else:
                return flag

    def check_reg(self, email):  # email values from request.form
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT * FROM users WHERE email = '%(email)s';")
        flag = False
        if query:
            if email == query['email']:
                flag = True
                return flag
        return flag

    def check_name(self, first_name,
                   last_name):  # first & last name from request.form
        flag = False
        name = [first_name, last_name]
        while True:
            if (len(name[0]) < 2 or len(name[1]) < 2):
                flag = True
                return flag
            elif not re.search("[a-z]", name[0]) or not re.search(
                    "[a-z]", name[1]):
                flag = True
                return flag
            elif (not re.search("[A-Z]", name[0])
                  or not re.search("[A-Z]", name[1])):
                flag = True
                return flag
            elif (re.search("[0-9]", name[0]) or re.search("[0-9]", name[1])):
                flag = True
                return flag
            elif (re.search("[_@$]", name[0]) or re.search("[_@$]", name[1])):
                flag = True
                return flag
            else:
                return flag

    def pin_owner(self, user_id, pin_id):
        flag = True
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT * FROM pins WHERE id = %(pin_id)s")
        if query:
            if query[0]["user_id"] == user_id:
                flag = False
                return flag 
        return flag

    def pin_check(self, form, check_type):
        flag = False
        if check_type == "new":
            if form["user_id"] == "":
                flag = True
                return flag
            if form["post"] == "":
                flag = True
                return flag
            if form["go"] == "":
                form["go"] = None
            if form["avoid"] == "":
                form["avoid"] = None
            if form["picture"] == "":
                form["picture"] = "default_pin.jpg"
            return form
        elif check_type == "update":
            if form["pin_id"] == "":
                flag = True
                return flag
            if form["user_id"] == "":
                flag = True
                return flag
            if form["post"] == "":
                flag = True
                return flag
            if form["go"] == "" or form["go"] == None:
                form["go"] = None
            if form["avoid"] == "" or form["avoid"] == None:
                form["avoid"] = None
            if form["picture"] == "" or form["picture"] == None:
                form["picture"] = "default_pin.jpg"
            return form
        else:
            flag = True
            return flag

    def user_check(self, email, password):  # does user exist
        flag = True
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT id, email, password FROM users WHERE email = '%(email)s';"
        )
        if query:
            flag = False
            return flag
        return flag


# QuerySearch queries the db
class QuerySearch:
    def user_add(self, form):  # add user to db
        if form["avatar"] == "":
            form["avatar"] = "default.jpg"
        try:
            mysql = connectToMySQL("travel_bug")
            query = "INSERT INTO users (first_name, last_name, email, password, avatar) VALUES ('%(first_name)s', '%(last_name)s', '%(email)s', '%(password)s', '%(avatar)s');"
            data = {
                "first_name": form["first_name"],
                "last_name": form["last_name"],
                "email": form["email"].lower(),
                "password": form["password"],
                "avatar": form["avatar"]
            }
            add_user = mysql.query_db(query, data)
            mysql = connectToMySQL("travel_bug")
            user = mysql.query_db(
                "SELECT id, first_name, last_name, email, avatar FROM users;")
            return user
        except:
            return False

    def pin_all(self):  # gets 10 most recent pins
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT pins.post, pins.created_date, pins.updated_date, pins.go, pins.avoid, pins.picture, users.first_name, users.last_name, locations.location FROM pins LEFT JOIN users ON pins.user_id = users.id LEFT JOIN locations ON pins.location_id = locations.id SORT BY pins.created_date DESC LIMIT 10;"
        )
        # print(query)
        return query

    def users_table(self):
        print(request.form)
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT id, email, first_name, last_name FROM users;")
        return query

    def pin_new(self, form):
        validated = Validator.pin_check(form, "new")
        if validated:
            return validated
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT location FROM locations;")
        if validated["location"] not in query:
            mysql = connectToMySQL("travel_bug")
            query = "INSERT INTO locations (location) VALUE ('%(location)s');"
            data = {"location": validated['location']}
            location_add = mysql.query_db(query, data)
        mysql = connectToMySQL("travel_bug")
        query = "INSERT INTO pins (user_id, location_id, post, go, avoid, picture) VALUES ('%(user_id)s', '%(location_id)s', '%(email)s', '%(picture)s');"
        data = {
            "user_id": validated["user_id"],
            "location_id": location_add,
            "post": validated["post"],
            "go": validated["go"],
            "avoid": validated["avoid"],
            "picture": validated["picture"]
        }
        pin_add = mysql.query_db(query, data)
        return False

    def user_pins(self, user_id):  # get users 10 most recent pins
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT pins.post, pins.created_date, pins.updated_date, pins.go, pins.avoid, pins.picture, users.first_name, users.last_name, locations.location FROM pins LEFT JOIN users ON pins.user_id = users.id LEFT JOIN locations ON pins.location_id = locations.id WHERE pins.user_id = %(user_id)s SORT BY pins.created_date DESC LIMIT 10;"
        )
        return query

    def user_get(self, user_id):
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT * FROM users WHERE users.id = %(user_id)s;")
        return query

    def pin_get(self, pin_id):
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT * FROM pins WHERE id = %(pin_id)s;")
        return query

    def pin_delete(self, user_id, pin_id):
        flag = True
        if Validator.pin_owner(user_id, pin_id):
            return flag
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT * FROM pins WHERE id = %(pin_id)s;")
        if query["user_id"] == user_id:
            flag = False
            mysql = connectToMySQL("travel_bug")
            query = mysql.query_db("SET SQL_SAFE_UPDATES = 0;")
            mysql = connectToMySQL("travel_bug")
            query = mysql.query_db(
                "DELETE FROM pins WHERE pins.id = %(pin_id)s;")
            mysql = connectToMySQL("travel_bug")
            query = mysql.query_db("SET SQL_SAFE_UPDATES = 1;")
            return flag
        return flag

    def pin_update(self, form):
        validated = Validator.pin_check(form, "update")
        if validated:
            return validated
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT location FROM locations;")
        if validated["location"] not in query:
            mysql = connectToMySQL("travel_bug")
            query = "INSERT INTO locations (location) VALUE ('%(location)s');"
            data = {"location": validated['location']}
            location_add = mysql.query_db(query, data)
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SET SQL_SAFE_UPDATES = 0;")
        mysql = connectToMySQL("travel_bug")
        query = "UPDATE pins SET location_id = %(location_id)s, post = '%(post)s', go = '%(go)s', avoid = '%(avoid)s', updated_date = NOW(), picture = '%(picture)s' WHERE pins.id = %(pin_id)s;"
        data = {
            "pin_id": validated["pin_id"],
            "location_id": location_add,
            "post": validated["post"],
            "go": validated["go"],
            "avoid": validated["avoid"],
            "picture": validated["picture"]
        }
        pin_update = mysql.query_db(query, data)
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SET SQL_SAFE_UPDATES = 1;")
        return False
