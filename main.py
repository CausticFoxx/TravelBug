from flask import session, render_template, request, redirect
import flask, secrets, random

app=flask.Flask(__name__)
app.secret_key = "keepitsecretkeepitsafe"
@app.route("/")
def index():
  return render_template('base_header.html')

# @app.route("/process_money", methods=['post'])
# def check():
#   print(request.form)
#   print(session["rnd_num"])
#   if int(session["rnd_num"]) < int(request.form["number_guess"]):
#     session["classname"] = "red"
#     session["message"] = "Too High!"
#   elif int(session["rnd_num"]) > int(request.form["number_guess"]):
#     session["classname"] = "red"
#     session["message"] = "Too Low!"
#   elif int(session["rnd_num"]) == int(request.form["number_guess"]):
#     session["classname"] = "green"
#     session["message"] = "Correct!"
#   else:
#     session["classname"] = "red"
#     session["message"] = "how did you break this?"
    
#   return render_template('index.html', classname=session["classname"], message=session["message"])

# @app.route("/reset")
# def reset():
#   session.pop("rnd_num")
#   return redirect("/")


if __name__=="__main__":
  app.run(debug=True)