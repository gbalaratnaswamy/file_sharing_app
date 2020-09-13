from flask import Flask, request, redirect, render_template, url_for, abort
from flask_pymongo import PyMongo
from flask.views import MethodView
import cfg
import encryption.encryption as encrypt

app = Flask(__name__)
app.config["MONGO_URI"] = cfg.DATABASE_URL
app.config["MAX_CONTENT_PATH"] = cfg.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = cfg.DEFAULT_UPLOAD_FOLDER
mongo = PyMongo(app)

import auth.api as auth
import db.models as db
from files.files_blueprint import files_blueprint
import files.files_manager as fm


@app.route('/')
def hello_world():
    return 'Hello World!'


class SingUP(MethodView):
    def get(self):
        if auth.check_user() is not None:
            return redirect("/dashboard")
        return render_template("signup.html", error=request.values.get("error"))

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        if "target" in request.cookies:
            target = request.cookies.get("target")
        else:
            target = "/dashboard"
        try:
            user, response = auth.signup_user(email, password, target)
        except auth.errors.UserExistError:
            return redirect(f"/signup?error=account with {email} already exist try <a href='/login'>login</a>")
        return response


class Login(MethodView):
    def get(self):
        if auth.check_user() is not None:
            return redirect("/dashboard")
        return render_template("login.html", error=request.values.get("error"))

    def post(self):
        email = request.form["email"]
        password = request.form["password"]
        if "target" in request.cookies:
            target = request.cookies.get("target")
        else:
            target = "/dashboard"
        try:
            user, val = auth.login_user(email, password, target)
        except db.errors.NoUserError:
            return redirect(url_for("login", error=f"there is no email with {email} try <a href='/signup>signup</a>"))
        except auth.errors.WrongPasswordError:
            return redirect(url_for("login", error="you have entered wrong password"))
        return val


class UpdateUser(MethodView):
    def get(self):
        user = auth.check_user()
        if user is None:
            return redirect("/login")
        return render_template("user_info.html", user=user)

    def post(self, value):
        print("yes")
        user = auth.check_user()
        if user is None:
            return redirect("/login")
        if value not in ["name", "password"]:
            return abort(404)
        if value == "name":
            user.name = request.form["name"]
            return redirect(url_for("update", info=" your name updated successfully"))
        if not encrypt.check_password(request.form["old_password"], user.password):
            return abort(404)
        user.password = encrypt.encrypt_password(request.form["password"])
        return redirect(url_for("update", info=" your password updated successfully"))


@app.route("/test")
def test():
    print(auth.check_user())
    return "hi"


@app.route("/dashboard")
def dashboard():
    user = auth.check_user()
    if user is None:
        return redirect("/login")
    return render_template("user_page.html", user=user, data=db.File.get_all_file(user.id))


@app.route("/logout")
def logout():
    return auth.logout_user("/login")


@app.template_filter()
def str_file_size(size):
    return fm.str_file_size(size)


app.add_url_rule('/signup', view_func=SingUP.as_view('signup'))
app.add_url_rule('/login', view_func=Login.as_view('login'))
app.add_url_rule('/update', view_func=UpdateUser.as_view('update'))
app.add_url_rule('/update/<value>', view_func=UpdateUser.as_view('updateUser'), methods=["POST"])
app.register_blueprint(files_blueprint)
if __name__ == '__main__':
    app.run()
