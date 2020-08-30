from flask import Flask, render_template, request, redirect, abort
from flask_pymongo import PyMongo
from cfg import *
from user_management import *
import cookies
import errors_and_info

app = Flask(__name__)
app.config["MONGO_URI"] = DATABASE_URL
mongo = PyMongo(app)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login(error=None):
    # if user post data
    if request.method == "POST":
        result = login_user(mongo.db[USER_COLLECTION], request.form["password"], request.form["email"])
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
    if check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/dashboard")
    # if user not already login
    return render_template("login.html", error=error)


@app.route("/signup", methods=["POST", "GET"])
def signup(error=None):
    if request.method == "POST":
        result = create_user(mongo.db[USER_COLLECTION], request.form["password"], request.form["email"])
        print(result)
        # if email already signup
        if result == "user_exist":
            return render_template("errors/error_page.html", email=request.form["email"])
        if result == "error":
            return abort(500)
        # if everything works fine
        return cookies.create_auth_cookie(mongo.db[AUTH_COLLECTION], request, "/dashboard")

    # if user requests login page
    # if user already login
    if check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/dashboard")
    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    if check_user(request,mongo.db[AUTH_COLLECTION]):
        return cookies.clear_auth_cookies(mongo.db[AUTH_COLLECTION], request)
    return redirect("/login")

# @app.route("/update_pass", methods=["POST", "GET"])
# def update_pass():
#     if request.method == "POST":
#         result = update_password()
#         if result == "wrong_password":
#             return render_template()
#         elif result == "success":
#             return render_template("")
#     else:
#         return render_template("update_pass.html")


@app.route("/dashboard")
def user_page():
    # check if user login
    result = check_user(request, mongo.db[AUTH_COLLECTION])
    # if not login redirect to login
    if not result:
        return render_template("login.html", error=errors_and_info.NOT_LOGIN_ERROR)
    return render_template("user_page.html")


@app.route("/test")
def testing_page():
    return abort(500)


if __name__ == '__main__':
    app.run(debug=True)
