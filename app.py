from flask import Flask, render_template, request, redirect, abort, url_for
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from cfg import *
import user_management as usrm
import cookies
import errors_and_info
from files_blueprint import files_blueprint
import os
from datetime import datetime
import files_manager as fm
import encryption

app = Flask(__name__)
app.config["MONGO_URI"] = DATABASE_URL
mongo = PyMongo(app)
app.register_blueprint(files_blueprint)
app.config["MAX_CONTENT_PATH"] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = "files"


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
    if usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return cookies.clear_auth_cookies(mongo.db[AUTH_COLLECTION], request)
    return redirect("/login")


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
    data = mongo.db[FILES_COLLECTION].find({"email": request.cookies.get("email")})
    return render_template("user_page.html", data=data)


@app.route("/test")
def testing_page():
    return redirect(url_for("login"))


@app.route("/userinfo")
def user_info():
    if not usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/loign")
    user = mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})
    return render_template("user_info.html", name=user["name"])


@app.route("/updatename", methods=["POST"])
def update_name():
    usrm.change_name(mongo.db[USER_COLLECTION], request.cookies.get("email"), request.form["newname"])
    return redirect("/userinfo")


@app.route('/filesupload', methods=['GET', 'POST'])
def upload_file():
    if not usrm.check_user(request, mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    if request.method == 'POST':
        f = request.files['file']
        user = mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})
        file_name = secure_filename(f.filename)
        file_type = fm.get_file_type(file_name)
        file_name = file_name.rsplit('.', 1)[0]
        if file_type not in ALLOWED_EXTENSIONS:
            return render_template("files_upload.html", error="files not supported")
        file_path = os.path.join(f"files/{user['email']}/", file_name)
        if not os.path.exists(f"files/{user['email']}"):
            os.mkdir(f"files/{user['email']}")
        f.save(file_path)
        file_size = os.stat(file_path).st_size
        size_consumed = user.get("size_consumed", 0)
        if size_consumed + file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            return render_template("files_upload.html",
                                   error=f"files size exceed you have already consumed {fm.modify_file_size(size_consumed)} new "
                                         f"file size is {fm.modify_file_size(file_size)}")
        mongo.db[FILES_COLLECTION].insert_one({"email": user["email"],
                                               "file_name": file_name,
                                               "file_type": file_type,
                                               "created_at": datetime.now(),
                                               "file_size": file_size,
                                               "file_hash": encryption.generate_file_hash(),
                                               "is_active": True,
                                               "file_path": "files/" + file_name})
        size_consumed += file_size
        mongo.db[USER_COLLECTION].update_one({"_id": user["_id"]},
                                             {"$set": {"size_consumed": size_consumed,
                                                       "updated_at": datetime.now()}})
        return redirect("/dashboard")
    return render_template("files_upload.html")


if __name__ == '__main__':
    app.run(debug=True)
