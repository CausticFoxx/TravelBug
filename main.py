from flask import Flask, render_template, redirect, request, session, flash, url_for
#from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
import server
from server import MySQLConnection, Validator, connectToMySQL, QuerySearch
app=Flask(__name__)
app.secret_key = "keepitsecretkeepitsafe"
bcrypt = Bcrypt(app)
import re

#EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
#pass_valid = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*?^])[a-zA-z0-9!@#$%&*?^]+$')

MySQLConnection('travel_bug')
connectToMySQL('travel_bug')
Validator = Validator()
QuerySearch = QuerySearch()

#render login/registration page
@app.route("/")
def registration():
      return render_template("login_register.html")

#registers user
@app.route("/register", methods=['GET','POST'])
def register():
      is_valid = True

      first_name = request.form['f-name']
      last_name = request.form['l-name']
      email = request.form['email']
      password = request.form['password']
      confirm_password = request.form['password-c']

      username_failed = Validator.check_name(first_name, last_name)
      password_failed = Validator.check_pw(password=password, confirm_pw=confirm_password)
      if username_failed == True: #if check_username fails, set is_valid to False
            is_valid = False
            flash("First or last name does not meet requirements")
      if password_failed == True: #if check_password fails, set is_valid to False
            is_valid = False 
            flash("Passwords must match and be a minimum of 8 characters long containing one lowercase, one uppercase, one number and one special character")
      #if all validations pass, insert info into users database and retrieve from database
      if(username_failed == False and password_failed == False):
            form = [first_name, last_name, email, password]
            new_user = QuerySearch.user_add(form)
            if new_user:
                  user_data = new_user[0]
                  session['user_id'] = user_data['id']
                  user_id = session['user_id']

      if is_valid == False:
            return redirect("/")
      if is_valid == True:
            return redirect(url_for("profile", user_id=user_id)) #redirect to profile

#logins in user
@app.route("/login", methods=['POST'])
def login():
      is_valid = True
      #checks to make sure email is entered
      email = request.form['email']
      password = request.form['password']
      user_data = Validator.check_reg(email, password)
      if user_data:
            session['user_id'] = user_data['id']
            user_id = session['user_id']
      else:
            is_valid = False
            flash("Email or password incorrect")
      if is_valid == False:
            return redirect("/")
      if is_valid == True:
            return redirect(url_for("profile", user_id=user_id)) #redirect to profile

#render newsfeed html
@app.route("/newsfeed")
def newsfeed():
      all_pins = QuerySearch.pin_all()
      #check if user is in session for add pin form
      if 'user_id' in session:
            user_id = session['user_id']
            return render_template("newsfeed.html", all_pins=all_pins, user_id=user_id)
      else:
            return render_template("newsfeed.html", all_pins=all_pins)

#adds pin
@app.route("/addpin/<user_id>", methods=['POST'])
def addPin(user_id):
      is_valid = True
      
      user_id = session['user_id']
      location = request.form['location']
      post = request.form['description']
      go = request.form['visit']
      avoid = request.form['avoid']
      form = [user_id, location, post, go, avoid]
      new_pin = QuerySearch.pin_new(form)
      return redirect(url_for("profile", user_id=user_id)) #redirect to profile

# edits pin when form is submitted
@app.route("/pin/edit/<pin_id>", methods = ['POST'])
def edit_pin(pin_id):
      #select from db using user_id and pin_id
      pin_id = pin_id
      user_id = session['user_id']
      location = request.form['location']
      post = request.form['description']
      go = request.form['visit']
      avoid = request.form['avoid']
      form = [pin_id, user_id, location, post, go, avoid]
      pin_edit = QuerySearch.pin_update(form)
      print("PIN EDIT")
      print(pin_edit)
      return redirect(url_for("profile", user_id=user_id)) #redirect to profile

      #check validations for new information submitted
      #if validations fail
#            flash("") #flash messages based on what failed
      #if validations passed
#            flash("Pin updated successfully")
            #query database to update specific pin
#      return redirect(url_for('profile') #returns to profile page or newsfeed?


#deletes pin from db
@app.route("/delete/pin/<pin_id>", methods =['GET','POST'])
def deletePin(pin_id):
      #delete pin from db
      user_id = session['user_id']
      delete_pin = QuerySearch.pin_delete(user_id, pin_id)
      print("IS PIN DELETED")
      print(delete_pin)
      return redirect(url_for("profile", user_id=user_id)) #redirect to profile


#render profile page html
@app.route("/profile/<user_id>")
def profile(user_id):
      #if user is not in session, return to registration/login page
      if 'user_id' not in session:
            return redirect("/")
      else:
            session_user_id = session['user_id']
            #find users pins
            user_pins = QuerySearch.user_pins(user_id)
            #find users data
            user_data = QuerySearch.user_get(user_id)
            return render_template("profile.html", user_id=session_user_id, user_pins=user_pins, user_data=user_data[0])

#edit profile html page
#@app.route("/profile/edit/<user_id>", methods=['POST', 'GET'])
#def edit_profile_page(user_id):
      #if user is not in session, return to registration/login page
#      if 'user_id' not in session:
#            return redirect("/")
      #query database to find if user exists, select first instance (should only be one)
      #send user information to edit profile html
#      return render_template("EDITPROFILE_HTML", user_data=user_data) #sends user_data to html page

#actually edits user when form is submitted
#@app.route("/edit/profile/<user_id>", methods = ['POST'])
#def edit_profile(user_id):
      #select from db using user_id
      #check validations for new information submitted
      #if validations fail
#            flash("") #flash messages based on what failed
      #if validations passed
#            flash("Profile updated successfully")
            #query database to update specific user
#      return redirect(url_for('profile') #returns to profile page

#logs out user
@app.route("/logout")
def logout():
      session.clear()
      return redirect("/")

if __name__=="__main__":
  app.run(debug=True)