from flask import Flask, render_template, request, redirect
from pymongo import MongoClient

app = Flask(__name__)
cluster=MongoClient(port=27017)

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
        return request.form["email"]
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
