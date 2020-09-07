from flask import Blueprint, abort, render_template, send_file, redirect, request
import app
import os
from cfg import FILES_COLLECTION, AUTH_COLLECTION, ALLOWED_EXTENSIONS, USER_COLLECTION, MAX_FILE_SIZE
from datetime import datetime
import user_management as usrm
from bson import ObjectId
import encryption
import files_manager as fm
from werkzeug.utils import secure_filename

files_blueprint = Blueprint('example_blueprint', __name__)


@files_blueprint.route('/files/<file_index>/<file_name>')
def index(file_index, file_name):
    file_name = file_name.rsplit('-', 1)[0]
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(file_index), "file_name": file_name})
    if file is None:
        return abort(404)
    if not file["is_active"]:
        return abort(404)
    return render_template("display_file.html", file=file, hash=file_index)


@files_blueprint.route("/files/<file_index>/download/<file_name>")
def download(file_index, file_name):
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(file_index),
                                                    "file_name": file_name.rsplit('.', 1)[0]})
    if file is None:
        return abort(404)
    if not file["is_active"]:
        return abort(404)
    return send_file(file["file_path"], attachment_filename=file_name)


@files_blueprint.route("/files/<file_index>/delete/<file_name>")
def delete_file(file_index, file_name):
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    file_name = file_name.rsplit('-', 1)[0]
    user = app.mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})
    file = app.mongo.db[FILES_COLLECTION].find_one({"_id": ObjectId(file_index), "file_name": file_name})
    if file is None:
        return abort(404)
    if not file["is_active"]:
        return abort(404)
    if request.cookies.get("email") != file["email"]:
        return abort(403)
    os.remove(file["file_path"])
    app.mongo.db[FILES_COLLECTION].update_one({"_id": file["_id"]}, {"$set": {"is_active": False}})
    app.mongo.db[USER_COLLECTION].update_one({"_id": user["_id"]},
                                             {"$set": {"size_consumed": user["size_consumed"]-file["file_size"],
                                                       "updated_at": datetime.now()}})
    return "delete successful"


@files_blueprint.route('/filesupload', methods=['GET', 'POST'])
def upload_file():
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    if request.method == 'POST':
        f = request.files['file']
        user = app.mongo.db[USER_COLLECTION].find_one({"email": request.cookies.get("email")})
        file_name = secure_filename(f.filename)
        file_type = app.fm.get_file_type(file_name)
        file_name = file_name.rsplit('.', 1)[0]
        file_size = int(request.form["size"])
        size_consumed = user.get("size_consumed", 0)
        if size_consumed + file_size > MAX_FILE_SIZE:
            return render_template(
                "files_upload.html",
                error=f"files size exceed you have already consumed {fm.modify_file_size(size_consumed)} new file "
                      f"size is {fm.modify_file_size(file_size)}")
        if file_type not in ALLOWED_EXTENSIONS:
            return render_template("files_upload.html", error="files not supported")
        file_hash = encryption.generate_file_hash()
        file_path = os.path.join(f"files/{user['email']}/", file_hash + file_name + "." + file_type)
        if not os.path.exists(f"files/{user['email']}"):
            os.mkdir(f"files/{user['email']}")
        f.save(file_path)
        # if size send by browser and original file size differ something went wrong
        # (unsuccessful upload or user manipulate data)
        if file_size != os.stat(file_path).st_size:
            os.remove(file_path)
            return abort(400)
        app.mongo.db[FILES_COLLECTION].insert_one({"email": user["email"],
                                                   "file_name": file_name,
                                                   "file_type": file_type,
                                                   "created_at": datetime.now(),
                                                   "file_size": file_size,
                                                   "file_hash": file_hash,
                                                   "is_active": True,
                                                   "file_path": file_path})
        size_consumed += file_size
        app.mongo.db[USER_COLLECTION].update_one({"_id": user["_id"]},
                                                 {"$set": {"size_consumed": size_consumed,
                                                           "updated_at": datetime.now()}})
        return redirect("/dashboard")
    return render_template("files_upload.html")

