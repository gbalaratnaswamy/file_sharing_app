from flask import Blueprint, abort, render_template, send_file, redirect, request
import files_manager as f
import app
from cfg import FILES_COLLECTION, AUTH_COLLECTION
import user_management as usrm

files_blueprint = Blueprint('example_blueprint', __name__)


@files_blueprint.route('/files/<hash>/<file_name>')
def index(hash, file_name):
    file_name = file_name.rsplit('-', 1)[0]
    print(file_name)
    file = app.mongo.db[FILES_COLLECTION].find_one({"file_hash": hash, "file_name": file_name})
    print(file)
    if file is None:
        return abort(404)
    if not file["is_active"]:
        return abort(404)
    print(file)
    return render_template("display_file.html", file=file, hash=hash)


@files_blueprint.route("/files/<hash>/download/<file_name>")
def download(hash, file_name):
    if not usrm.check_user(request, app.mongo.db[AUTH_COLLECTION]):
        return redirect("/login")
    file = app.mongo.db[FILES_COLLECTION].find_one({"file_hash": hash,
                                                    "file_name": file_name.rsplit('.', 1)[0].lower()})
    print(file)
    return send_file(f"files/{file['email']}/{file_name}", attachment_filename=file_name)


@files_blueprint.route("/files/<email>/delete/<file_name>")
def delete_file(email, file_name):
    file = app.mongo.db[FILES_COLLECTION].find_one({"email": email, "file_name": file_name})
    return str(file["file_size"])
