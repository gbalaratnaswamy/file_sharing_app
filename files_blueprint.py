from flask import Blueprint, abort, render_template, send_file, redirect, request
import files_manager as f
import app
import os
from cfg import FILES_COLLECTION, AUTH_COLLECTION
import user_management as usrm
from bson import ObjectId

files_blueprint = Blueprint('example_blueprint', __name__)


@files_blueprint.route('/files/<indx>/<file_name>')
def index(indx, file_name):
    file_name = file_name.rsplit('-', 1)[0]
    print(file_name)
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(indx), "file_name": file_name})
    print(file)
    if file is None:
        return abort(404)
    if not file["is_active"]:
        return abort(404)
    print(file)
    return render_template("display_file.html", file=file, hash=indx)


@files_blueprint.route("/files/<indx>/download/<file_name>")
def download(indx, file_name):
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(indx),
                                                    "file_name": file_name.rsplit('.', 1)[0]})
    return send_file(file["file_path"], attachment_filename=file_name)


@files_blueprint.route("/files/<indx>/delete/<file_name>")
def delete_file(indx, file_name):
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    file_name = file_name.rsplit('-', 1)[0]
    print(file_name)
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(indx), "file_name": file_name})
    if request.cookies.get("email") != file["email"]:
        return abort(403)
    os.remove(file["file_path"])
    return "delete sucessful"
