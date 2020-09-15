import encryption.encryption as encrypt
from werkzeug.utils import secure_filename
from cfg import FILE_HASH_LENGTH


class NotAllowedError(Exception):
    pass


def get_file_info(f):
    file_name = secure_filename(f.filename)
    file_name, file_type = file_name.rsplit('.', 1)
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
