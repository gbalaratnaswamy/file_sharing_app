import encryption
from flask import make_response, redirect
from cfg import AUTH_COOKIE_DURATION


# create cookie token and add to database
def create_auth_cookie(collection, request, redirect_url):
    response = make_response(redirect(redirect_url))
    random_string = encryption.create_cookie_auth(collection)
    response.set_cookie("email", request.form["email"], max_age=AUTH_COOKIE_DURATION,
                        httponly=True, samesite="Strict")
    response.set_cookie("token", random_string, max_age=AUTH_COOKIE_DURATION,
                        httponly=True, samesite="Strict")
    collection.insert_one({"email": request.form["email"], "token": encryption.encrypt_string(random_string)})
    return response


def clear_auth_cookies(collection, request):
    response = make_response(redirect("/login"))
    response.delete_cookie("email")
    token = request.cookies.get("token")
    response.delete_cookie("token")
    collection.delete_one({"token": encryption.encrypt_string(token)})
    return response
