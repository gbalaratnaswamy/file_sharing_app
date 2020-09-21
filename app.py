from flask import Flask, request, redirect, render_template, url_for, abort, session
from flask_pymongo import PyMongo
from flask.views import MethodView
import cfg
from datetime import datetime
import encryption.encryption as encrypt

app = Flask(__name__)
app.config["MONGO_URI"] = cfg.DATABASE_URL
app.config["MAX_CONTENT_PATH"] = cfg.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = cfg.DEFAULT_UPLOAD_FOLDER
mongo = PyMongo(app)
app.secret_key = "idnegeos"

import auth.api as auth
import db.models as db
from files.files_blueprint import files_blueprint
import files.files_manager as fm


@app.route('/')
def index():
    user = auth.check_user()
    return render_template("index.html", user=user)


class SingUP(MethodView):
    def get(self):
        if auth.check_user() is not None:
            return redirect("/dashboard")
        return render_template("signup.html", error=session.pop("error", None))

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        if "target" in request.cookies:
            target = request.cookies.get("target")
        else:
            target = "/dashboard"
        try:
            user = auth.signup_user(email, password)
        except auth.errors.UserExistError:
            session["error"] = f"account with {email} already exist try <a href='/login'>login</a>"
            return redirect(f"/signup")
        return redirect(target)


class Login(MethodView):
    def get(self):
        if auth.check_user() is not None:
            return redirect("/dashboard")
        return render_template("login.html", error=session.pop("error", None))

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        if "target" in request.cookies:
            target = request.cookies.get("target")
        else:
            target = "/dashboard"
        try:
            user = auth.login_user(email, password)
        except db.errors.NoUserError:
            session["error"] = f"there is no email with {email} try <a href='/signup>signup</a>"
            return redirect(url_for("login"))
        except auth.errors.WrongPasswordError:
            session["error"] = "you have entered wrong password"
            return redirect(url_for("login"))
        return redirect(target)


class UpdateUser(MethodView):
    def get(self):
        user = auth.check_user()
        if user is None:
            return redirect("/login")
        return render_template("user_info.html", user=user, error=session.pop("error", None))

    def post(self, value):
        user = auth.check_user()
        if user is None:
            return redirect("/login")
        if value not in ["name", "password", "plans"]:
            return abort(404)
        if value == "name":
            user.name = request.form["name"]
            session["info"] = "your name updated successfully"
            return redirect(url_for("update"))
        if value == "plans":
            return "Comming soon"
            # try:
            #     plan = int(request.form["plan"])
            # except ValueError:
            #     return abort(500)
            # if plan not in [1, 2, 3]:
            #     return abort(500)
            # plans_data = [350, 400, 450]
            # user.max_size = plans_data[plan - 1] * 1024 * 1024
            # return redirect("/update")
        if not encrypt.check_password(request.form["old_password"], user.password):
            session["error"] = "wrong password"
            return redirect(url_for("update"))
        user.password = encrypt.encrypt_password(request.form["password"])
        session["info"] = "your password updated successfully"
        return redirect(url_for("update"))


# @app.route("/test")
# def test():
# print(request.cookies)
# print(auth.check_user())

# @app.route("/test2")
# def test2():
#     return render_template("test.html")

@app.route("/dashboard")
def dashboard():
    user = auth.check_user()
    if user is None:
        return redirect("/login")
    return render_template("dashboard.html", user=user, data=db.File.get_all_file(user.id),
                           info=session.pop("info", None))


@app.route("/logout")
def logout():
    auth.logout_user()
    return redirect("/login")


@app.template_filter()
def str_file_size(size):
    return fm.str_file_size(size)


@app.template_filter()
def str_date(date):
    difference = datetime.now() - date
    return f"{difference.days} days"


@app.template_filter()
def str_to_mb(size):
    return fm.str_to_mb(size)


@app.template_filter()
def icon_file_type(file_type):
    return fm.icon_file_type(file_type)


@app.template_filter()
def cut_file_name(file_name):
    return fm.cut_file_name(file_name)


app.add_url_rule('/signup', view_func=SingUP.as_view('signup'))
app.add_url_rule('/login', view_func=Login.as_view('login'))
app.add_url_rule('/update', view_func=UpdateUser.as_view('update'))
app.add_url_rule('/update/<value>', view_func=UpdateUser.as_view('updateUser'), methods=["POST"])
app.register_blueprint(files_blueprint)
if __name__ == '__main__':
    app.run()
