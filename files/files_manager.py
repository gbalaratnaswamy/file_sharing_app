import encryption.encryption as encrypt
from werkzeug.utils import secure_filename
from cfg import FILE_HASH_LENGTH, ALLOWED_FILE_EXTENSIONS


class NotAllowedError(Exception):
    pass


def get_file_info(f):
    file_name = secure_filename(f.filename)
    file_name, file_type = file_name.rsplit('.', 1)
    file_type = file_type.lower()
    print(file_type)
    if file_type not in ALLOWED_FILE_EXTENSIONS:
        raise NotAllowedError
    return file_name, file_type


def generate_file_hash():
    return encrypt.generate_random_string(FILE_HASH_LENGTH)


def str_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} bytes"
    size /= 1024
    if size < 1024:
        return f"{size:.2f} KB"
    size /= 1024
    if size < 1024:
        return f"{size:.2f} MB"
    size /= 1024
    return f"{size:.2f} GB"


def str_to_mb(size: int) -> str:
    size /= 1024 * 1024
    return f"{size:.2f}"


def icon_file_type(file_type: str):
    # icons={"image":"fa fa-file-picture-o",
    #        "pdf":}
    file_type = file_type.lower()
    if file_type == "pdf":
        return ''' <i class ="fa fa-file-pdf-o" style="font-size:24px" > </i> '''
    if file_type in ["png", "jpg", "jpeg"]:
        return ''' <i class ="fa fa-file-picture-o" style="font-size:24px" > </i>'''
    if file_type == "txt":
        return '''<i class ="fa fa-file-text-o" style="font-size:24px" > </i>'''
    if file_type in ["doc", "docx"]:
        return '''<i class ="fa fa-file-word-o" style="font-size:24px" > </i>'''
    if file_type in ["ppt", "pptx"]:
        return '''<i class ="fa fa-file-powerpoint-o" style="font-size:24px" > </i>'''
    if file_type in ["xls", "csv"]:
        return '''<i class ="fa fa-file-excel-o" style="font-size:24px" > </i>'''
    else:
        return '''<i class ="fa fa-file-o" style="font-size:24px" > </i>'''


def cut_file_name(file_name: str, val=15):
    # file_name, file_type = file_name.rsplit('.', 1)
    if len(file_name) > val:
        return file_name[:val] + '...'
    return file_name
