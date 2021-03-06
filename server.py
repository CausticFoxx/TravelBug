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
            elif not re.search("[!@#$%&*?]", password):
                flag = True
                return flag
            elif re.search("\s", password):
                flag = True
                return flag
            else:
                return flag


    def check_reg(self, email, password):  # email values from request.form
        mysql = connectToMySQL("travel_bug")
        query = "SELECT * FROM users WHERE email = %(email)s"
        data = {
            "email": email
        }
        result = mysql.query_db(query, data)
        #if email was found, check password
        if result:
            user_data = result[0]
            if user_data["password"] == password:
                return user_data
            else:
                return False

        return result

    def check_name(self, first_name="",
                   last_name=""):  # first & last name from request.form
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
        flag = False
        mysql = connectToMySQL("travel_bug")
        query = "SELECT pins.user_id FROM pins WHERE id = %(pin_id)s"
        data = {
            "pin_id": pin_id
        }
        result = mysql.query_db(query, data)
        user = [sub['user_id'] for sub in result]
        if (user == [user_id]):
            flag = True
            return flag
        else:
            return flag
        
    def pin_check(self, form, check_type):
        flag = False
        if check_type == "new":
            if form[0] == "":
                flag = True
                return flag
            if form[1] == "":
                flag = True
                return flag
            if form[2] == "":
                form[2] = None
                return flag
            if form[3] == "":
                form[3] = None
            if form[4] == "":
                form[4] = None
            if form[5] == "":
                form[5] = "default_pin.jpg"
            return flag
        elif check_type == "update":
            if form[0] == "":
                flag = True
                return flag
            if form[1] == "":
                flag = True
                return flag
            if form[2] == "":
                flag = True
                return flag
            if form[3] == "":
                flag = True
                return flag
            if form[4] == "" or form[4] == None:
                form[4] = None
            if form[5] == "" or form[5] == None:
                form[5] = None
            return flag
        else:
            flag = True
            return flag

    def user_check(self, email, password):  # does user exist
        flag = True
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT id, email, password FROM users WHERE email = %(email)s;"
        )
        if query:
            flag = False
            return flag
        return flag


# QuerySearch queries the db
class QuerySearch:
    def user_add(self, form):  # add user to db
        #if form[avatar] == "":
        #    form[avatar] = "default.jpg"

        mysql = connectToMySQL('travel_bug')
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s)"
        data = {
            "first_name": form[0],
            "last_name": form[1],
            "email": form[2].lower(),
            "password": form[3]
        }
        add_user = mysql.query_db(query, data)

        mysql = connectToMySQL("travel_bug")
        query = "SELECT id, first_name, last_name, email FROM users WHERE email = %(email)s"
        data = {
            "email": form[2]
        }
        user = mysql.query_db(query, data)

        return user

    def pin_all(self):  # gets 10 most recent pins
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db(
            "SELECT pins.id, pins.post, pins.location_id, pins.user_id, pins.created_date, pins.go, pins.avoid, pins.picture, users.id, users.first_name, users.last_name, locations.id, locations.location FROM pins LEFT JOIN users ON pins.user_id = users.id LEFT JOIN locations ON pins.location_id = locations.id ORDER BY pins.created_date DESC LIMIT 10"
        )
        print(query)
        return query

    def pin_new(self, form): #sends to validations and adds new pin
        not_validated = Validator.pin_check(self, form, "new")
        if not_validated == True:
            return False #pin did not get added
        else:
            mysql = connectToMySQL("travel_bug")
            query = "SELECT * FROM locations WHERE location = %(location)s"
            data = {
                "location" : form[1]
            }
            location_exist = mysql.query_db(query, data)
            if location_exist:
                mysql = connectToMySQL("travel_bug")
                query = "SELECT id FROM locations WHERE location = (%(location)s)"
                data = {
                    "location": form[1]
                }
                location = mysql.query_db(query, data)
                location_id = [ sub['id'] for sub in location]
            else:
                mysql = connectToMySQL("travel_bug")
                query = "INSERT INTO locations (location) VALUES (%(location)s)"
                data = {
                    "location": form[1]
                    }
                location_id = mysql.query_db(query, data)
            mysql = connectToMySQL("travel_bug")
            query = "INSERT INTO pins (user_id, location_id, post, go, avoid, picture) VALUES (%(user_id)s, %(location_id)s, %(post)s, %(go)s, %(avoid)s, %(picture)s)"
            data = {
                "user_id": form[0],
                "location_id": location_id,
                "post": form[2],
                "go": form[3],
                "avoid": form[4],
                "picture": form[5]
            }
            pin_add = mysql.query_db(query, data)
            return pin_add

    def user_pins(self, user_id):  # get users 10 most recent pins
        mysql = connectToMySQL("travel_bug")
        data = {
            'user_id': user_id
        }
        query = mysql.query_db(
            "SELECT pins.id, pins.post, pins.created_date, pins.updated_date, pins.go, pins.avoid, pins.picture, users.first_name, users.last_name, locations.location FROM pins LEFT JOIN users ON pins.user_id = users.id LEFT JOIN locations ON pins.location_id = locations.id WHERE pins.user_id = %(user_id)s ORDER BY pins.created_date DESC LIMIT 10;",
            data
        )
        return query

    def user_get(self, user_id):
        mysql = connectToMySQL("travel_bug")
        query = "SELECT * FROM users WHERE id = %(user_id)s"
        data = {
            "user_id": user_id
        }
        result = mysql.query_db(query, data)
        return result

    def pin_get(self, pin_id):
        mysql = connectToMySQL("travel_bug")
        query = mysql.query_db("SELECT * FROM pins WHERE id = %(pin_id)s;")
        return query

    def pin_delete(self, user_id, pin_id):
        flag = True
        pin_owner_verify = Validator.pin_owner(self, user_id = user_id, pin_id=pin_id)
        if (pin_owner_verify == True):
            mysql = connectToMySQL("travel_bug")
            query = "DELETE FROM pins WHERE id = %(pin_id)s"
            data = {
                "pin_id": pin_id
            }
            delete_pin = mysql.query_db(query, data)
            return flag
        else:
            flag = False
            return flag
        
    def pin_update(self, form):
        not_validated = Validator.pin_check(self, form, "update")
        if not_validated == True:
            return False
        else:
            mysql = connectToMySQL("travel_bug")
            query = "UPDATE pins  SET post = %(post)s, go = %(go)s, avoid = %(avoid)s WHERE id = (%(pin_id)s)"
            data = {
                "post": form[3],
                "go": form[4],
                "avoid": form[5],
                #"picture":
                "pin_id": form[0]
            }
            pin_edit = mysql.query_db(query, data)
            if pin_edit:
                return True
            else:
                return False

    def user_edit(self, form):
        mysql = connectToMySQL("travel_bug")
        query = "UPDATE users  SET about_me = %(about)s, avatar = %(avatar)s WHERE id = (%(user_id)s)"
        data = {
            "about": form[0],
            "avatar": form[1],
            "user_id": form[2],
        }
        user_edit = mysql.query_db(query, data)
        if user_edit:
            return True
        else:
            return False
