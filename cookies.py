import encryption
from flask import make_response, redirect


def create_auth_cookie(collection, request, redirect_url):
    response = make_response(redirect(redirect_url))
    random_string = encryption.create_cookie_auth(collection)
    response.set_cookie("email", request.form["email"])
    response.set_cookie("token", random_string)
    collection.insert_one({"email": request.form["email"], "token": random_string})
    return response


def clear_auth_cookies():
    pass