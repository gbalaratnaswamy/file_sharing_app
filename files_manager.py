

def create_file(collection,file_name,email):
    collection.insert_one({"email":email})