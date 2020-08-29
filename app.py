from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from cfg import *
from user_management import *

app = Flask(__name__)
cluster=MongoClient(port=27017)
db=cluster[DATABASE_NAME]

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == "POST":
        return "II"
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        result= create_user(db[USER_COLLECTION],request.form["password"],request.form["email"])
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
