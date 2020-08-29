# user info : email, password


def create_user(collection, password: str, email: str):
    # if user already exists
    if collection.find_one({"email": email}) is not None:
        return "user_exist"
    else:
        try :
            collection.insert_one({"email": email,
                                   "password": password})
            return "success"
        except:
            return "error"
