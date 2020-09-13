import bcrypt
import hashlib
import jwt
import cfg
import string
import random

ascii_letters = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters


def encrypt_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


def encrypt_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def encode_token_jwt(payload):
    jwt_encode = jwt.encode(payload, cfg.SECRET_KEY)
    return jwt_encode


def generate_session_id():
    return generate_random_string(cfg.SESSION_ID_LENGTH)


def decode_token_jwt(token):
    return jwt.decode(token, cfg.SECRET_KEY)


def generate_random_string(length: int):
    return "".join(random.choice(ascii_letters) for i in range(length))
