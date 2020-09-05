from flask import Flask, render_template, request, redirect, abort, url_for
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename

from cfg import *

app = Flask(__name__)
app.config["MONGO_URI"] = DATABASE_URL
app.config["MAX_CONTENT_PATH"] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = "files"
mongo = PyMongo(app)

import user_management as usrm
import cookies
import errors_and_info
from files_blueprint import files_blueprint
import os
from datetime import datetime
import files_manager as fm
import encryption

app.register_blueprint(files_blueprint)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login(error=None):
    # if user post data
    if request.method == "POST":
        result = usrm.login_user(mongo.db[USER_COLLECTION], request.form["password"], request.form["email"])
        # if user login successfully
        if result == "success":
            return cookies.create_auth_cookie(mongo.db[AUTH_COLLECTION], request, "/dashboard")
        # if there is no account with given email
        elif result == "no_account":
            return render_template("login.html", error=errors_and_info.no_account_error(request.form["email"]))
        # if user types wrong password
        elif result == "wrong_pass":
            return render_template("login.html", error=errors_and_info.WRONG_PASS_ERROR)

    # if user requests page (get)
    # if user already login
    if usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/dashboard")
    # if user not already login
    return render_template("login.html", error=error)


@app.route("/signup", methods=["POST", "GET"])
def signup(error=None):
    if request.method == "POST":
        result = usrm.create_user(mongo.db[USER_COLLECTION], request.form["password"], request.form["email"])
        # if email already signup
        if result == "user_exist":
            return render_template("errors/error_page.html", email=request.form["email"])
        if result == "error":
            return abort(500)
        # if everything works fine
        return cookies.create_auth_cookie(mongo.db[AUTH_COLLECTION], request, "/dashboard")

    # if user requests login page
    # if user already login
    if usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/dashboard")
    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    return cookies.clear_auth_cookies(mongo.db[AUTH_COLLECTION], request)


@app.route("/updatepass", methods=["POST", "GET"])
def update_pass():
    if request.method == "POST":
        result = usrm.update_password(request.cookies.get("email"), request.form["old_pass"], request.form["new_pass"],
                                      mongo.db[USER_COLLECTION])
        if result == "wrong_pass":
            return render_template("update_pass.html", error="wrong password")
        elif result == "success":
            return redirect("/dashboard")
        elif result == "error":
            return abort(500)
    else:
        if not usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
            return redirect("/login")
        return render_template("update_pass.html", error=None)


@app.route("/dashboard")
def user_page():
    # check if user login
    result = usrm.check_user(request, mongo.db[AUTH_COLLECTION])
    # if not login redirect to login
    if not result:
        return render_template("login.html", error=errors_and_info.NOT_LOGIN_ERROR)
    data = mongo.db[FILES_COLLECTION].find({"email": request.cookies.get("email"), "is_active": True})
    user = mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})
    return render_template("user_page.html", data=data, user=user)


@app.route("/test")
def testing_page():
    return redirect(url_for("login"))


@app.route("/userinfo")
def user_info():
    if not usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    user = mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})

    return render_template("user_info.html", name=user["name"])


@app.route("/updatename", methods=["POST"])
def update_name():
    usrm.change_name(mongo.db[USER_COLLECTION], request.cookies.get("email"), request.form["newname"])
    return redirect("/userinfo")


if __name__ == '__main__':
    app.run(debug=True)

@app.template_filter("file_size_str")
def file_size_str(s):
    return str(fm.modify_file_size(int(s)))