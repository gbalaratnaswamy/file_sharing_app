from flask import request, redirect, render_template, Blueprint, url_for, abort, make_response, send_file
import db.models as db
import auth.api as auth
from . import files_manager
import os
import cfg
from datetime import datetime
from bson import ObjectId

files_blueprint = Blueprint('example_blueprint', __name__)


@files_blueprint.route('/files/view/<file_index>/<file_name>')
def view_file(file_index, file_name):
    user = auth.check_user()
    if user is None:
        response = make_response(redirect("/login"))
        response.set_cookie("target", f"/files/view/{file_index}/{file_name}")
        return response
    try:
        file = db.File.find_file({"_id": ObjectId(file_index), "file_name": file_name})
    except db.errors.NoFileError:
        return abort(404)
    if not file.active:
        return "file removed"
    return render_template("display_file.html", file=file, user=user)

    #


#
@files_blueprint.route("/files/download/<file_index>/<file_name>")
def download_file(file_index, file_name):
    user = auth.check_user()
    if user is None:
        response = make_response(redirect("/login"))
        response.set_cookie("target", f"/files/view/{file_index}/{file_name}")
    try:
        file = db.File.find_file({"_id": ObjectId(file_index)})
        if file.file_name + "." + file.file_type != file_name:
            return abort(404)
    except db.errors.NoFileError:
        return abort(404)
    file.downloads = user.email
    try:
        return send_file(file.path, attachment_filename=file_name)
    except FileNotFoundError:
        return abort(404)


@files_blueprint.route("/files/delete/<file_index>/<file_name>")
def delete_file(file_index, file_name):
    user = auth.check_user()
    if user is None:
        return redirect(url_for("login", error="you must login to delete"))
    try:
        file = db.File.find_file({"_id": ObjectId(file_index), "file_name": file_name})
    except db.errors.NoFileError:
        return abort(404)
    if user.id != file.user_id:
        return abort(400)
    os.remove(file.path)
    file.set_is_active(False)
    user.size -= file.size
    return redirect("/dashboard")


@files_blueprint.route('/files/upload', methods=['GET', 'POST'])
def upload_file():
    pass
    user = auth.check_user()
    if user is None:
        return redirect(url_for("login", error="please login"))
    if request.method == "GET":
        return render_template("files_upload.html", error=request.values.get("error"), user=user)
    f = request.files["file"]
    try:
        file_name, file_type = files_manager.get_file_info(f)
        file_size = int(request.form["size"])
    except files_manager.NotAllowedError:
        return redirect(url_for("upload_file",
                                error="file type not supported"))
    size_consumed = user.size + file_size
    if size_consumed > cfg.MAX_FILE_SIZE:
        return redirect(url_for("upload_file",
                                error=f"you don't have enough space your file has {files_manager.str_file_size(file_size)} but you only have {files_manager.str_flie_size(user.size)}"))
    file_hash = files_manager.generate_file_hash()
    file_path = os.path.join(f"{cfg.DEFAULT_UPLOAD_FOLDER}/{user.email}/", file_hash + file_name + "." + file_type)
    if not os.path.exists(f"{cfg.DEFAULT_UPLOAD_FOLDER}/{user.email}"):
        os.mkdir(f"{cfg.DEFAULT_UPLOAD_FOLDER}/{user.email}")
    f.save(file_path)
    if file_size != os.stat(file_path).st_size:
        os.remove(file_path)
        return abort(400)
    db.File.create_file(f.filename, file_size, file_path, file_hash, file_type, user.id)
    user.size += file_size
    return redirect("/dashboard")


@files_blueprint.route("/files/history/<file_index>/<file_name>")
def file_history(file_index, file_name):
    print("h0")
    user = auth.check_user()
    if user is None:
        return redirect(url_for("login"))
    try:
        file = db.File.find_file({"_id": ObjectId(file_index), "file_name": file_name})
    except db.errors.NoFileError:
        return abort(404)
    return render_template("file_view.html", file=file, user=user)
