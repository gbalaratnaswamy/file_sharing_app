# user info : email, password`
import encryption
import pymongo.errors as mongoerror
from datetime import datetime


# create new user in database
def create_user(collection, password: str, email: str):
    # if user already exists
    if collection.find_one({"email": email}) is not None:
        return "user_exist"
    else:
        try:
            collection.insert_one({"email": email,
                                   "password": encryption.encrypt_string(password),
                                   "name": None,
                                   "created_at": datetime.now(),
                                   "last_login_date": datetime.now(),
                                   "updated_at": datetime.now(),
                                   "size_consumed": 0})
            return "success"
        # if failed to insert
        except (mongoerror.ConnectionFailure, mongoerror.NetworkTimeout):
            return "error"


# check credentials
def login_user(collection, password: str, email: str):
    user = collection.find_one({"email": email})
    # if there is no account
    if user is None:
        return "no_account"
    # if password is wrong
    if user["password"] != encryption.encrypt_string(password):
        return "wrong_pass"
    collection.update_one({"email": email}, {"$set": {"last_login_date": datetime.now()}})
    return "success"


# def logout_user(collection,request):
#     pass


def update_password(email, old_pass, new_pass, collection):
    user = collection.find_one({"email": email})
    if user is None:
        return "error"
    if user["password"] == encryption.encrypt_string(old_pass):
        collection.update_one({"email": email}, {"$set": {"password": encryption.encrypt_string(new_pass)}})
        return "success"
    return "wrong_pass"


# check if user is already login
def check_user(request, collection) -> bool:
    # if email and token data not in cookies
    if "email" not in request.cookies:
        return False
    if "token" not in request.cookies:
        return False
    token = collection.find_one(
        {"token": encryption.encrypt_string(request.cookies.get("token")), "email": request.cookies.get("email")})
    # if no token in database with cookie data
    if token is None:
        return False
    return True


def change_name(collection, email, new_name):
    collection.update_one({"email": email}, {"$set": {"name": new_name}})
