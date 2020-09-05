def create_file(collection, file_name, email):
    collection.insert_one({"email": email})


def get_file_type(filename):
    if "." in filename:
        return filename.rsplit('.', 1)[1].lower()


def modify_file_size(file_size):
    if file_size < 1024:
        return f"{file_size} bytes"
    file_size /= 1024
    if file_size < 1024:
        return f"{file_size:.2f} kb"
    return f"{file_size / 1024:.2f} mb"
