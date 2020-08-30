# user info : email, password`
import encryption

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


def login_user(collection, password: str, email: str):
    user = collection.find_one({"email": email})
    if user is None:
        return "no_account"
    if user["password"] != encryption.encrypt_string(password):
        return "wrong_pass"
    return "success"


def logout_user(collection, email: str):
    pass


def update_password():
    pass


def check_user(request, collection) -> bool:
    if "email" not in request.cookies:
        return False
    if "token" not in request.cookies:
        return False
    token = collection.find_one({"token": encryption.encrypt_string(request.cookies.get("token"))})
    if token is None:
        return False
    if token['email'] == request.cookies.get("email"):
        return True
    return False


