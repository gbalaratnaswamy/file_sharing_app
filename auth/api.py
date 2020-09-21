import db.models as db
from . import errors
from flask import session
import encryption.encryption as encrypt
import jwt


def login_user(email, password):
    user = db.User.find_user({"email": email})
    if user is None:
        raise errors.NoUserError
    if not encrypt.check_password(password, user.password):
        raise errors.WrongPasswordError
    __CookiesLogin.create_token(user)
    return user


def logout_user():
    __CookiesLogin.clear_cookies()


def signup_user(email, password):
    try:
        db.User.find_user({"email": email})
    except db.errors.NoUserError:
        user = db.User.create_user(email, encrypt.encrypt_password(password))
        __CookiesLogin.create_token(user)
        return user,
    raise errors.UserExistError


def check_user():
    if "_token" not in session:
        return None
    token = __CookiesLogin.validate_token()
    if token is None:
        return None
    user = db.User.find_user({"email": token["email"]})
    # if request.cookies.get("session_id") in user.session_id:
    return user


class __CookiesLogin:
    @staticmethod
    def create_token(user):
        token = encrypt.encode_token_jwt({"email": user.email,
                                          "name": user.name})

        # # token still in cookie for template recognision
        # response.set_cookie("_token", "yes", httponly=True)
        session["_token"] = token
        session_id = encrypt.generate_session_id()
        db.AuthTokens.create_token(user.name, session_id)

    @staticmethod
    def validate_token():
        token = session["_token"]
        try:
            data = encrypt.decode_token_jwt(token)
        except(jwt.exceptions.InvalidSignatureError, jwt.exceptions.ExpiredSignatureError):
            return None
        return data

    @staticmethod
    def clear_cookies():
        session.clear()
