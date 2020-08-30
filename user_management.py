# user info : email, password`
import encryption


# create new user in database
def create_user(collection, password: str, email: str):
    # if user already exists
    if collection.find_one({"email": email}) is not None:
        return "user_exist"
    else:
        try:
            collection.insert_one({"email": email,
                                   "password": encryption.encrypt_string(password)})
            return "success"
        # if failed to insert
        except:
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
    return "success"


def logout_user(collection, email: str):
    pass


def update_password(email, old_pass, new_pass, collection):
    user = collection.find_one({"email": email})
    if user is None:
        return "error"
    if user["password"] == encryption.encrypt_string(old_pass):
        collection.update_one({"email":email},{"$set":{"password":encryption.encrypt_string(new_pass)}})
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
