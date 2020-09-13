import db.models as db
from . import errors
from flask import make_response, request, redirect
import encryption.encryption as encrypt
import jwt


def login_user(email, password, target):
    user = db.User.find_user({"email": email})
    if user is None:
        raise errors.NoUserError
    if not encrypt.check_password(password, user.password):
        raise errors.WrongPasswordError
    return user, __CookiesLogin.create_token(target, user)


def logout_user(target):
    return __CookiesLogin.clear_cookies(target)


def signup_user(email, password, target):
    try:
        db.User.find_user({"email": email})
    except db.errors.NoUserError:
        user = db.User.create_user(email, encrypt.encrypt_password(password))
        return user, __CookiesLogin.create_token(target, user)
    raise errors.UserExistError


def check_user():
    if "_token" not in request.cookies:
        return None
    token = __CookiesLogin.validate_token()
    if token is None:
        return None
    user = db.User.find_user({"email": token["email"]})
    # if request.cookies.get("session_id") in user.session_id:
    return user


class __CookiesLogin:
    @staticmethod
    def create_token(target, user):
        token = encrypt.encode_token_jwt({"email": user.email,
                                          "name": user.name})
        db.AuthTokens.create_token(user.name, token)
        response = make_response(redirect(target))
        response.set_cookie("_token", token, httponly=True)
        session_id = encrypt.generate_session_id()
        # user.session_id = session_id
        response.set_cookie("session_id", session_id)
        return response

    @staticmethod
    def validate_token():
        token = request.cookies.get("_token")
        token = token.encode()
        try:
            data = encrypt.decode_token_jwt(token)
        except(jwt.exceptions.InvalidSignatureError, jwt.exceptions.ExpiredSignatureError):
            return None
        return data

    @staticmethod
    def clear_cookies(target):
        response = make_response(redirect(target))
        response.delete_cookie("_token")
        return response
