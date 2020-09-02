from flask import Blueprint,abort
import files_manager as f
files_blueprint = Blueprint('example_blueprint', __name__)

@files_blueprint.route('/files/<file_name>')
def index(file_name):
    if file_name in ["noo","yes"]:
        return str(file_name)
    return abort(404)


